#include "pch.hpp"
#include "texture_compressor.hpp"
#include "resmgr/multi_file_system.hpp"
#include "resmgr/bwresource.hpp"
#include "texture_manager.hpp"
#include "texture_lock_wrapper.hpp"
#include "render_context.hpp"
#include "texture_loader.hpp"
#include "cstdmf/string_builder.hpp"
#include "moo/texture_detail_level.hpp"

#define ENABLE_NVTT !(BW_EXPORTER || CONSUMER_CLIENT_BUILD || _MSC_VER >= 1900)

#if ENABLE_NVTT
#include "nvtt/nvtt.h"
#ifdef _DEBUG
#ifdef _M_AMD64
#pragma message( __FILE__ " Linking nvtt_Debug_noCuda_x64.lib" )
#pragma comment( lib, "nvtt_Debug_noCuda_x64.lib" )
#else // _M_AMD64
#pragma message( __FILE__ " Linking nvtt_Debug_noCuda_Win32.lib" )
#pragma comment( lib, "nvtt_Debug_noCuda_Win32.lib" )
#endif // _M_AMD64
#else // _DEBUG
#ifdef _M_AMD64
#pragma message( __FILE__ " Linking nvtt_Release_noCuda_x64.lib" )
#pragma comment( lib, "nvtt_Release_noCuda_x64.lib" )
#else // _M_AMD64
#pragma message( __FILE__ " Linking nvtt_Release_noCuda_Win32.lib" )
#pragma comment( lib, "nvtt_Release_noCuda_Win32.lib" )
#endif // _M_AMD64
#endif // _DEBUG
#endif // ENABLE_NVTT

DECLARE_DEBUG_COMPONENT2("Moo", 0)


BW_BEGIN_NAMESPACE

#ifndef CODE_INLINE
#include "texture_compressor.ipp"
#endif

namespace Moo
{

#ifndef SAFE_RELEASE
#define SAFE_RELEASE(p)      { if(p) { (p)->Release(); (p)=NULL; } }
#endif

	// -----------------------------------------------------------------------------
	// Section: Texture compressor helper functions
	// -----------------------------------------------------------------------------

	namespace
	{

		int	calcMipChainLength(uint width, uint height)
		{
			int numMips = 0;
			// caclulate number of mips in the full mip chain
			uint size = std::max(width, height);
			while (size > 0)
			{
				size /= 2;
				numMips++;
			}
			return numMips;
		}

		bool	canReuseSource(const ComObjectWrap<DX::Texture>& texture,
			D3DFORMAT format, uint numMips, uint dstWidth, uint dstHeight)
		{
			MF_ASSERT(texture);

			uint numLevels = texture->GetLevelCount();

			D3DSURFACE_DESC desc;
			HRESULT hr = texture->GetLevelDesc(0, &desc);
			MF_ASSERT(SUCCEEDED(hr));

			if (numMips == 0)
			{
				numMips = calcMipChainLength(dstWidth, dstHeight);
			}
			//  return false if source texture is not lockable
			bool bLockable = (desc.Usage & D3DUSAGE_DYNAMIC ||
				desc.Pool != D3DPOOL_DEFAULT);
			bool bParamMatch = (numLevels > 0 && numLevels == numMips &&
				desc.Format == format);

			return (bLockable && bParamMatch);
		}

		/**
		 *	This function returns true if the format is a DX9 block-compressed
		 *	format. Block compression requires power-of-two surfaces on DX9
		 *	class hardware.
		 */
		bool	isBlockCompressedFormat(D3DFORMAT format)
		{
			return format == D3DFMT_DXT1 ||
				format == D3DFMT_DXT2 ||
				format == D3DFMT_DXT3 ||
				format == D3DFMT_DXT4 ||
				format == D3DFMT_DXT5;
		}

#if ENABLE_NVTT
		/**
		*	This function converts source texture to in-memory dds file using
		*   NVidia texture tools library.
		*
		*	@returns			Pointer to created binary block, NULL otherwise
		*
		*/
		bool	isFormatNVTTSupported(D3DFORMAT format)
		{
			return (format == D3DFMT_A8R8G8B8 ||
				format == D3DFMT_DXT1 ||
				format == D3DFMT_DXT3 ||
				format == D3DFMT_DXT5);
		}

		BinaryPtr compressToMemoryNVTT(
			const BW::string& srcTextureName,
			const SmartPointer<TextureDetailLevel>& dstInfo,
			D3DFORMAT format,
			bool effNoResize,
			uint effMipCount)
		{
			BW_GUARD;

			if (!rc().device())
			{
				return NULL;
			}

			// setup nvtt options
			nvtt::Format nvttFormat;
			switch (format)
			{
			case D3DFMT_A8R8G8B8:	nvttFormat = nvtt::Format_RGBA; break;
			case D3DFMT_DXT1:		nvttFormat = nvtt::Format_DXT1; break;
			case D3DFMT_DXT3:		nvttFormat = nvtt::Format_DXT3; break;
			case D3DFMT_DXT5:		nvttFormat = nvtt::Format_DXT5; break;
			default:
			{
				// NVTT does not support destination format
				return NULL;
			}
			}

			ComObjectWrap<DX::Texture> srcTexture;
			// load source texture
			BinaryPtr bin =
				BWResource::instance().rootSection()->readBinary(srcTextureName);

			D3DXIMAGE_INFO srcInfo;

			if (bin)
			{
				// Create the DX texture, using D3DX to support legacy formats
				// tell d3dx not to upscale non power 2 textures
				// this way we can use nvtt for upscaling if required
				srcTexture = rc().createTextureFromFileInMemoryEx(
					bin->data(), bin->len(),
					D3DX_DEFAULT, D3DX_DEFAULT, 1, 0, D3DFMT_A8R8G8B8,
					D3DPOOL_SCRATCH, D3DX_FILTER_NONE,
					D3DX_FILTER_NONE, 0, &srcInfo, NULL);
			}

			if (!srcTexture.hasComObject())
			{
				// failed to load source texture
				ASSET_MSG("compressToMemoryNVTT - failed to load source texture %s\n",
					srcTextureName.c_str());
				return NULL;
			}


			// setup nvtt options
			nvtt::InputOptions inputOptions;
			nvtt::CompressionOptions compressionOptions;
			nvtt::OutputOptions outputOptions;

			inputOptions.setTextureLayout(nvtt::TextureType_2D, srcInfo.Width,
				srcInfo.Height, 1);

			if (dstInfo->maxExtent() > 0)
			{
				inputOptions.setMaxExtents(dstInfo->maxExtent());
			}

			if (!effNoResize)
			{
				// upscale to the next power of 2 to support old hardware
				inputOptions.setRoundMode(nvtt::RoundMode_ToNextPowerOfTwo);
			}
			else if ((nvttFormat == nvtt::Format_DXT1 ||
				nvttFormat == nvtt::Format_DXT3 ||
				nvttFormat == nvtt::Format_DXT5) &&
				((srcInfo.Width & 0x3) || (srcInfo.Height & 0x3)))
			{
				WARNING_MSG("TextureCompressor: DXT format only support width/height \
				to be multiple of 4. Using uncompressed format instead.\n");
				nvttFormat = nvtt::Format_RGBA;
			}


			nvtt::AlphaMode alphaMode = nvtt::AlphaMode_None;
			if (nvttFormat == nvtt::Format_RGBA || nvttFormat == nvtt::Format_DXT3 ||
				nvttFormat == nvtt::Format_DXT5)
			{
				alphaMode = nvtt::AlphaMode_Transparency;
			}
			inputOptions.setAlphaMode(alphaMode);

			if (dstInfo->normalMap())
			{
				// we have some data in the alpha channel
				// what we gonna do is to move it to the blue channel
				inputOptions.setNormalMap(true);
				inputOptions.setAlphaMode(nvtt::AlphaMode_None);
				if (nvttFormat == nvtt::Format_DXT1)
				{
					compressionOptions.setColorWeights(1.0f, 1.0f, 0.0f);
				}
				else if (nvttFormat == nvtt::Format_DXT5)
				{
					nvttFormat = nvtt::Format_DXT5n;
				}
			}

			compressionOptions.setFormat(nvttFormat);
			compressionOptions.setQuality(nvtt::Quality_Normal);

			// fill binary data
			TextureLockWrapper textureLock(srcTexture);
			D3DLOCKED_RECT lockedRect;

			HRESULT hr = textureLock.lockRect(0, &lockedRect, NULL, 0);
			if (FAILED(hr))
			{
				ASSET_MSG("compressToMemoryNVTT - failed to lock source texture %s\n",
					srcTextureName.c_str());
				return NULL;
			}

			D3DSURFACE_DESC realTexDesc;
			srcTexture->GetLevelDesc(0, &realTexDesc);

			// real texture width and hight might be bigger
			// if source texture does not have power 2 dimensions
			// we need to check this case and extract part of the source texture

			// get desired number of mip levels
			// it might be too big, we still need to calculate real number
			int numMips = (int)effMipCount;
			if (dstInfo->sourceMipmaps() == TextureDetailLevel::SOURCE_NO_MIPMAPS)
			{
				inputOptions.setTextureLayout(nvtt::TextureType_2D, srcInfo.Width,
					srcInfo.Height, 1);
				// set the whole image as mip 0
				inputOptions.setMipmapDataRect(lockedRect.pBits, 0, 0,
					srcInfo.Width, srcInfo.Height,
					realTexDesc.Width, realTexDesc.Height, 1, 0, 0);

				int numRealMips = calcMipChainLength(srcInfo.Width, srcInfo.Height);
				if (numMips == 0 || numMips > numRealMips)
				{
					// generate full mipchain
					numMips = numRealMips;
				}
			}
			else
			{
				// we have prebaked mipmap chain
				// read all of them and fill nvtt mipmap data
				// we assume that image is square and the rest of it is a mipchain
				uint32 mipSize = 0;
				int chainSpace = 0;
				bool horizontal = (dstInfo->sourceMipmaps() ==
					TextureDetailLevel::SOURCE_HORIZONTAL_MIPMAPS);

				if (horizontal)
				{
					// horizontal mipchain
					mipSize = srcInfo.Height;
					MF_ASSERT(srcInfo.Width >= srcInfo.Height &&
						srcInfo.Height * 2 >= srcInfo.Width);
					chainSpace = srcInfo.Width;
				}
				else
				{
					// vertical mipchain
					mipSize = srcInfo.Width;
					MF_ASSERT(srcInfo.Height >= srcInfo.Width &&
						srcInfo.Width * 2 >= srcInfo.Height);
					chainSpace = srcInfo.Height;
				}
				inputOptions.setTextureLayout(nvtt::TextureType_2D, mipSize,
					mipSize, 1);

				uint32 x0 = 0;
				uint32 y0 = 0;
				int numRealMips = 0;
				// supply nvtt with the mipchain data
				// at the end of the loop mipSize might be bigger than 0
				// which will indicate that we have incomplete mipchain
				while (mipSize >= 1 && chainSpace > 0)
				{
					inputOptions.setMipmapDataRect(lockedRect.pBits, x0, y0,
						x0 + mipSize, y0 + mipSize, realTexDesc.Width, realTexDesc.Height,
						1, 0, numRealMips);
					if (horizontal)
					{
						x0 += mipSize;
					}
					else
					{
						y0 += mipSize;
					}
					numRealMips++;
					chainSpace -= mipSize;
					mipSize /= 2;
				}

				// update number of mipmaps
				// we only update number of mipmaps if provided number is too big
				if (numRealMips < numMips || numMips == 0)
				{
					numMips = numRealMips;
				}
			}

			hr = textureLock.unlockRect(0);
			textureLock.flush();
			textureLock.fini();
			MF_ASSERT(SUCCEEDED(hr));

			srcTexture = NULL;

			// nvtt won't regenerate mip level if we supplied data for it
			// setup up number mipmaps required, filter and alpha mode
			inputOptions.setMipmapGeneration(true, numMips);
			inputOptions.setMipmapFilter(nvtt::MipmapFilter_Kaiser);

			// output memory handler
			struct MemoryOutputHandler : nvtt::OutputHandler
			{
				// preallocate memory
				MemoryOutputHandler(size_t reqSize)
				{
					binary_.reserve(reqSize);
				}
				/// Indicate the start of a new compressed image
				// that's part of the final texture.
				virtual void beginImage(int size, int width, int height,
					int depth, int face, int miplevel)
				{	// ignore
				}

				/// Output data. Compressed data is output as soon
				// as it's generated to minimize memory allocations.
				virtual bool writeData(const void* data, int size)
				{
					MF_ASSERT(size > 0);
					size_t oldSize = binary_.size();
					binary_.resize(oldSize + size);
					memcpy(&binary_[0] + oldSize, data, size);
					return true;
				}

				BW::vector<uint8>		binary_;
			};

			// Error handler
			struct ErrorReporter : nvtt::ErrorHandler
			{
				virtual void error(nvtt::Error e)
				{
					ERROR_MSG("compressToMemoryNVTT - NVTT:%s\n",
						nvtt::errorString(e));
				}
			};

			ErrorReporter		errorReporter;
			size_t reqDDSMemory = TextureLoader::calcDDSSize(
				format, srcInfo.Width, srcInfo.Height, numMips);
			MemoryOutputHandler	memoryOutputHandler(reqDDSMemory);

			// setup output options
			outputOptions.setOutputHandler(&memoryOutputHandler);
			outputOptions.setErrorHandler(&errorReporter);

			nvtt::Compressor compressor;
			bool bSuccess = compressor.process(inputOptions, compressionOptions,
				outputOptions);
			if (!bSuccess)
			{
				// nvtt error should be reported by ErrorReporter
				ASSET_MSG("TextureManager::convertToDDS- Failed to convert texture %s\n",
					srcTextureName.c_str());
				return NULL;
			}

			BinaryPtr outputBin = new BinaryBlock(&memoryOutputHandler.binary_[0],
				memoryOutputHandler.binary_.size(), "BinaryBlock/TextureCompressor");

			return outputBin;
		}

#endif // CONSUMER_CLIENT_BUILD
		/**
		 *	This function loads a texture using d3dx functionality.
		 *
		 *	The shape of the source decides the path:
		 *
		 *	1. A plain single image (sourceMipmaps() == SOURCE_NO_MIPMAPS).
		 *	   The image is mip 0 and any further levels are generated from
		 *	   it. noResize() keeps it at native dimensions; otherwise it
		 *	   is scaled to the nearest power of two first. mipCount() == 0
		 *	   means "full mip chain" - the same convention the nvtt path
		 *	   uses.
		 *
		 *	2. A prebaked mipchain stacked into one image (SOURCE_HORIZONTAL_MIPMAPS
		 *	   / SOURCE_VERTICAL_MIPMAPS). The levels are sliced out at native
		 *	   dimensions; nothing is generated or filtered.
		 *
		 *	@param	string	Texture name
		 *	@param	TextureDetailLevel	Texture detail level
		 *	@param	output uint	number of mipmaps
		 *
		 *	@return DX::Texture
		 */
		ComObjectWrap<DX::Texture> loadD3DXTexture(
			const BW::string& srcTextureName,
			const SmartPointer<TextureDetailLevel>& dstInfo,
			uint* pNumMips,
			bool effNoResize,
			uint effMipCount)
		{
			BW_GUARD;

			if (!rc().device())
			{
				return NULL;
			}

			*pNumMips = 0;
			// failed to read texture data
			BinaryPtr inputBin =
				BWResource::instance().rootSection()->readBinary(srcTextureName);
			if (!inputBin)
			{
				ASSET_MSG("loadD3DXTexture - could not read texture data %s\n",
					srcTextureName.c_str());
				return NULL;
			}

			// Load the source at its NATIVE dimensions. noResize handling and
			// level slicing both need the true image size, so the pow2 scaling
			// D3DX applies with D3DX_DEFAULT dims must not happen here. Plain
			// images that are allowed to resize are reloaded at pow2 dims below.
			ComObjectWrap<DX::Texture> tex = rc().createTextureFromFileInMemoryEx(
				inputBin->data(), inputBin->len(),
				D3DX_DEFAULT_NONPOW2, D3DX_DEFAULT_NONPOW2, 1, 0, D3DFMT_A8R8G8B8,
				D3DPOOL_SCRATCH, D3DX_FILTER_NONE, D3DX_FILTER_NONE, 0, NULL, NULL);
			if (!tex.hasComObject())
			{
				ASSET_MSG("loadD3DXTexture - failed to load source texture %s\n",
					srcTextureName.c_str());
				return NULL;
			}

			D3DSURFACE_DESC desc;
			HRESULT hr = tex->GetLevelDesc(0, &desc);
			if (FAILED(hr))
			{
				ASSET_MSG("loadD3DXTexture - failed to get level description "
					"for %s (hr=0x%x)\n", srcTextureName.c_str(), uint32(hr));
				return NULL;
			}

			uint32 width = desc.Width;
			uint32 height = desc.Height;

			if (dstInfo->sourceMipmaps() == TextureDetailLevel::SOURCE_NO_MIPMAPS)
			{
				// Plain single image source. It must never go through the
				// prebaked chain slicer: the legacy code fell into it for any
				// noResize / explicit mipCount rule, halved the image height,
				// copied zero pixels once the level count guard
				// (realMipCount < mipCount(), 0 < 0) went false, and saved an
				// empty black half-height dds product.
				if (!effNoResize &&
					((width & (width - 1)) != 0 || (height & (height - 1)) != 0))
				{
					// Resize to the nearest power of two, same policy the
					// nvtt path applies to non-noResize rules.
					tex = rc().createTextureFromFileInMemoryEx(
						inputBin->data(), inputBin->len(),
						D3DX_DEFAULT, D3DX_DEFAULT, 1, 0, D3DFMT_A8R8G8B8,
						D3DPOOL_SCRATCH, D3DX_FILTER_BOX | D3DX_FILTER_MIRROR,
						D3DX_FILTER_BOX | D3DX_FILTER_MIRROR, 0, NULL, NULL);
					if (!tex.hasComObject())
					{
						ASSET_MSG("loadD3DXTexture - failed to load source "
							"texture %s for pow2 resize\n",
							srcTextureName.c_str());
						return NULL;
					}
					hr = tex->GetLevelDesc(0, &desc);
					if (FAILED(hr))
					{
						ASSET_MSG("loadD3DXTexture - failed to get level "
							"description for %s (hr=0x%x)\n",
							srcTextureName.c_str(), uint32(hr));
						return NULL;
					}
					width = desc.Width;
					height = desc.Height;
				}

				// How many mip levels the product carries: the explicit
				// mipCount(), or the full chain for this size. mipCount() == 0
				// means full chain - the nvtt path convention.
				uint32 chainLength = (uint32)calcMipChainLength(width, height);
				uint32 numMips = effMipCount > 0
					? effMipCount
					: chainLength;
				// ... and never longer than the top level allows.
				if (numMips > chainLength)
				{
					numMips = chainLength;
				}

				ComObjectWrap<DX::Texture> outputTexture =
					rc().createTexture(width, height, numMips, 0,
						D3DFMT_A8R8G8B8, D3DPOOL_SCRATCH);
				if (!outputTexture.hasComObject())
				{
					ASSET_MSG("loadD3DXTexture - failed to create %ux%u %u level "
						"destination texture for %s\n",
						width, height, numMips, srcTextureName.c_str());
					return NULL;
				}

				DX::Surface* pSurfSrc = NULL;
				hr = tex->GetSurfaceLevel(0, &pSurfSrc);
				if (FAILED(hr) || !pSurfSrc)
				{
					ASSET_MSG("loadD3DXTexture - failed to get source surface "
						"level 0 of %s (hr=0x%x)\n",
						srcTextureName.c_str(), uint32(hr));
					return NULL;
				}

				DX::Surface* pSurfDest = NULL;
				hr = outputTexture->GetSurfaceLevel(0, &pSurfDest);
				if (FAILED(hr) || !pSurfDest)
				{
					ASSET_MSG("loadD3DXTexture - failed to get destination "
						"surface level 0 of %s (hr=0x%x)\n",
						srcTextureName.c_str(), uint32(hr));
					SAFE_RELEASE(pSurfSrc);
					return NULL;
				}

				{
					SimpleMutexHolder smh(rc().getD3DXCreateMutex());
					hr = D3DXLoadSurfaceFromSurface(pSurfDest, NULL, NULL,
						pSurfSrc, NULL, NULL, D3DX_FILTER_NONE, 0);
				}
				SAFE_RELEASE(pSurfDest);
				SAFE_RELEASE(pSurfSrc);
				if (FAILED(hr))
				{
					ASSET_MSG("loadD3DXTexture - failed to copy top level of "
						"%s (hr=0x%x)\n", srcTextureName.c_str(), uint32(hr));
					return NULL;
				}

				if (numMips > 1)
				{
					// Generate the remaining levels from the top level.
					SimpleMutexHolder smh(rc().getD3DXCreateMutex());
					hr = D3DXFilterTexture(outputTexture.pComObject(), NULL, 0,
						D3DX_FILTER_BOX | D3DX_FILTER_MIRROR);
					if (FAILED(hr))
					{
						ASSET_MSG("loadD3DXTexture - failed to generate mip "
							"chain for %s (hr=0x%x)\n",
							srcTextureName.c_str(), uint32(hr));
						return NULL;
					}
				}

				*pNumMips = numMips;
				return outputTexture;
			}

			// The source carries a prebaked mipchain stacked horizontally or
			// vertically inside one image: slice the levels out of it at the
			// native dimensions the file was loaded with.
			{
				uint32 newWidth = width;
				uint32 newHeight = height;
				uint32 mipBase = dstInfo->mipSize();

				if (dstInfo->sourceMipmaps() == TextureDetailLevel::SOURCE_HORIZONTAL_MIPMAPS)
				{
					newWidth = mipBase != 0
						? mipBase
						: newWidth / 2;
					mipBase = newWidth;
				}
				else
				{
					newHeight = mipBase != 0
						? mipBase
						: newHeight / 2;
					mipBase = newHeight;
				}

				uint32 levelWidth = newWidth;
				uint32 levelHeight = newHeight;
				uint32 levelOffset = 0;
				uint32 levelSize = mipBase;
				uint32 levelMax =
					dstInfo->sourceMipmaps() == TextureDetailLevel::SOURCE_HORIZONTAL_MIPMAPS
					? width
					: height;
				// mipCount() == 0 means the whole chain present in the image
				// (nvtt path convention). The legacy guard
				// realMipCount < dstInfo->mipCount() with mipCount() == 0 was
				// 0 < 0: the loop never ran and an empty texture was produced.
				uint32 mipLimit = effMipCount > 0
					? effMipCount
					: 0xffffffff;
				uint32 realMipCount = 0;
				while (levelWidth > 0 &&
					levelHeight > 0 &&
					realMipCount < mipLimit &&
					(levelSize + levelOffset) <= levelMax)
				{
					realMipCount++;
					levelHeight = levelHeight >> 1;
					levelWidth = levelWidth >> 1;
					levelOffset += levelSize;
					levelSize = levelSize >> 1;
				}

				if (realMipCount == 0)
				{
					// Nothing sliceable in this layout. Fail loudly instead
					// of producing an empty texture product.
					ASSET_MSG("loadD3DXTexture - %s declares a prebaked "
						"mipchain but no level fits the image layout\n",
						srcTextureName.c_str());
					return NULL;
				}

				ComObjectWrap<DX::Texture> outputTexture =
					rc().createTexture(newWidth, newHeight, realMipCount, 0,
						D3DFMT_A8R8G8B8, D3DPOOL_SCRATCH);
				if (!outputTexture.hasComObject())
				{
					ASSET_MSG("loadD3DXTexture - failed to create %ux%u %u level "
						"destination texture for %s\n",
						newWidth, newHeight, realMipCount,
						srcTextureName.c_str());
					return NULL;
				}

				DX::Surface* pSurfSrc = NULL;
				hr = tex->GetSurfaceLevel(0, &pSurfSrc);
				if (FAILED(hr) || !pSurfSrc)
				{
					ASSET_MSG("loadD3DXTexture - failed to get source surface "
						"level 0 of %s (hr=0x%x)\n",
						srcTextureName.c_str(), uint32(hr));
					return NULL;
				}

				bool copyFailed = false;
				{
					uint32 sliceWidth = newWidth;
					uint32 sliceHeight = newHeight;
					uint32 levelBase = 0;
					bool horizontal =
						dstInfo->sourceMipmaps() == TextureDetailLevel::SOURCE_HORIZONTAL_MIPMAPS;

					RECT srcRect;
					SimpleMutexHolder smh(rc().getD3DXCreateMutex());
					for (uint32 iLevel = 0; iLevel < realMipCount; iLevel++)
					{
						srcRect.top = horizontal ? 0 : levelBase;
						srcRect.bottom = srcRect.top + sliceHeight;
						srcRect.left = horizontal ? levelBase : 0;
						srcRect.right = srcRect.left + sliceWidth;
						levelBase += mipBase;
						sliceWidth = sliceWidth >> 1;
						sliceHeight = sliceHeight >> 1;
						mipBase = mipBase >> 1;

						DX::Surface* pSurfDest = NULL;
						HRESULT hr2 =
							outputTexture->GetSurfaceLevel(iLevel, &pSurfDest);
						if (FAILED(hr2) || !pSurfDest)
						{
							ASSET_MSG("loadD3DXTexture - failed to get "
								"destination surface level %u of %s "
								"(hr=0x%x)\n", iLevel, srcTextureName.c_str(),
								uint32(hr2));
							copyFailed = true;
							break;
						}
						hr2 = D3DXLoadSurfaceFromSurface(pSurfDest, NULL, NULL,
							pSurfSrc, NULL, &srcRect, D3DX_FILTER_NONE, 0);
						pSurfDest->Release();
						if (FAILED(hr2))
						{
							ASSET_MSG("loadD3DXTexture - failed to slice mip "
								"level %u out of %s (hr=0x%x)\n", iLevel,
								srcTextureName.c_str(), uint32(hr2));
							copyFailed = true;
							break;
						}
					}
				}
				SAFE_RELEASE(pSurfSrc);

				if (copyFailed)
				{
					return NULL;
				}

				*pNumMips = realMipCount;
				return outputTexture;
			}
		}

		/**
		 *	This method copies data from the source texture to destination texture
		 *  completing the mipchain if necessary
		 *
		 *	@param dstTexture	Destination texture. Can't be empty.
		 */
		static bool copyTexture(ComObjectWrap<DX::Texture>& dstTexture,
			const ComObjectWrap<DX::Texture>& srcTexture)
		{
			BW_GUARD;
			// both source and destination textures must exist
			MF_ASSERT(srcTexture.hasComObject());
			MF_ASSERT(dstTexture.hasComObject());

			DX::Texture* pmiptexSrc = srcTexture.pComObject();
			DX::Texture* pmiptexDest = dstTexture.pComObject();
			uint32			numSrcMipLevels = srcTexture->GetLevelCount();
			uint32			numDstMipLevels = dstTexture->GetLevelCount();

			HRESULT hr;
			DWORD srcMipMapLevel = 0;
			D3DSURFACE_DESC desc;


			DWORD	currMipLevel;

			// if we have fewer destination mipmap levels than the source, 
			//  it may be because we have specified a very low maxextent (dimensions)
			//	of the destination texture, which means only the smallest mipmaps 
			//	from the source texture will fit the maxextent requirements.
			if (numDstMipLevels < numSrcMipLevels)
			{
				// find the largest source mipmap level that corresponds to the max dimensions
				//  required for the destination texture, and set that as the starting mipmap
				//	level to copy into the destination.

				// get the dimensions of the destination mipmaps
				DX::Surface* pOriginalDestination = NULL;
				hr = pmiptexDest->GetSurfaceLevel(0, &pOriginalDestination);
				if (FAILED(hr) || !pOriginalDestination)
				{
					ERROR_MSG("TextureCompressor::copyTexture: failed to get the "
						"destination surface level 0 (hr = 0x%x). Out of memory?\n",
						uint32(hr));
					SAFE_RELEASE(pOriginalDestination);
					return false;
				}
				hr = pOriginalDestination->GetDesc(&desc);
				UINT largestDstMipMapDimension = max<UINT>(desc.Width, desc.Height);

				SAFE_RELEASE(pOriginalDestination); // reduce reference count on this dx resource so it can be freed

				// get the dimensions of the largest source mipmap
				DX::Surface* pOriginalSource = NULL;
				hr = pmiptexSrc->GetSurfaceLevel(0, &pOriginalSource);
				if (FAILED(hr) || !pOriginalSource)
				{
					ERROR_MSG("TextureCompressor::copyTexture: failed to get the "
						"source surface level 0 (hr = 0x%x). Out of memory?\n",
						uint32(hr));
					SAFE_RELEASE(pOriginalSource);
					return false;
				}
				hr = pOriginalSource->GetDesc(&desc);
				UINT largestSrcMipMapDimension = max<UINT>(desc.Width, desc.Height);

				SAFE_RELEASE(pOriginalSource); // reduce reference count on this dx resource so it can be freed

				UINT currDimension = largestSrcMipMapDimension;
				MF_ASSERT(currDimension); // assert if largest source tex mip size is zero.
				currMipLevel = 0;
				while (currDimension > largestDstMipMapDimension)
				{
					currDimension /= 2;
					++currMipLevel;
					if ((currDimension < 1) || (currMipLevel > numSrcMipLevels))
					{
						WARNING_MSG("Not enough mip maps in source texture to copy into destination of correct dimensions");
						currMipLevel = 0; // start src mipmap copying from the largest one
						break;
					}
				}

				srcMipMapLevel = currMipLevel;
			}
			else
				// If we have more destination than source mip levels, don't copy the last 
				// mip level in the source chain, as this one will be copied to scratch 
				// memory before being used as the source for further mip creation
				if (numDstMipLevels > numSrcMipLevels)
				{
					--numSrcMipLevels;
				}

			DWORD iLevel = 0;

			SimpleMutexHolder smh(rc().getD3DXCreateMutex());

			// copy the existing src mip levels that fit into the dest mip levels
			for (; iLevel < numDstMipLevels; ++iLevel)
			{
				DX::Surface* psurfSrc = NULL;
				DX::Surface* psurfDest = NULL;
				hr = pmiptexSrc->GetSurfaceLevel(srcMipMapLevel, &psurfSrc);
				if (FAILED(hr))
				{
					ERROR_MSG("TextureCompressor::copyTexture: failed to get the "
						"source surface level %d (hr = 0x%x). Out of memory?\n",
						srcMipMapLevel, uint32(hr));
					SAFE_RELEASE(psurfSrc);
					SAFE_RELEASE(psurfDest);
					return false;
				}
				hr = pmiptexDest->GetSurfaceLevel(iLevel, &psurfDest);
				if (FAILED(hr))
				{
					ERROR_MSG("TextureCompressor::copyTexture: failed to get the "
						"destination surface level %d (hr = 0x%x). Out of memory?\n",
						iLevel, uint32(hr));
					SAFE_RELEASE(psurfSrc);
					SAFE_RELEASE(psurfDest);
					return false;
				}
				hr = D3DXLoadSurfaceFromSurface(psurfDest, NULL, NULL,
					psurfSrc, NULL, NULL, D3DX_FILTER_TRIANGLE, 0);
				if (FAILED(hr))
				{
					ERROR_MSG("TextureCompressor::copyTexture: failed to copy mip "
						"level %d into the destination texture (hr = 0x%x). "
						"Out of memory?\n", iLevel, uint32(hr));
					SAFE_RELEASE(psurfSrc);
					SAFE_RELEASE(psurfDest);
					return false;
				}
				SAFE_RELEASE(psurfSrc);
				SAFE_RELEASE(psurfDest);
				++srcMipMapLevel;

				// if we have run out of src mipmap levels (because we had to start half way through 
				//	the source mip levels due to max dimension requirements of the destination texture,
				//	and I guess that not all mip levels were created for the source texture)
				//  stop copying them.
				if (srcMipMapLevel >= numSrcMipLevels)
					break;

				// if we have more source mip levels than we need in the dest tex, dont copy anymore
				if (iLevel >= numDstMipLevels)
					break;
			}


			// Now, create further desired mip map levels
			if (numDstMipLevels > numSrcMipLevels)
			{
				DX::Surface* psurfSrc[2] = { NULL, NULL };

				hr = D3D_OK;

				DX::Surface* pOriginalSource = NULL;
				bool guardFailed = false;

				do
				{
					hr = pmiptexSrc->GetSurfaceLevel(iLevel, &pOriginalSource);
					if (FAILED(hr) || !pOriginalSource)
					{
						guardFailed = true;
						ERROR_MSG("TextureCompressor::copyTexture: failed to get the "
							"source surface level %d for mip generation (hr = 0x%x). "
							"Out of memory?\n", iLevel, uint32(hr));
						break;
					}
					hr = pOriginalSource->GetDesc(&desc);

					D3DFORMAT intermediateFormat = desc.Format;

					// If our source format is one of the compressed formats, go via
					// an uncompressed format when creating the mipmaps
					if (intermediateFormat == D3DFMT_DXT1 || intermediateFormat == D3DFMT_DXT2 ||
						intermediateFormat == D3DFMT_DXT3 || intermediateFormat == D3DFMT_DXT4 ||
						intermediateFormat == D3DFMT_DXT5)
					{
						intermediateFormat = D3DFMT_A8R8G8B8;
					}

					// Create the source surface to use in scratch memory,
					// and load it with the desired mipmap
					hr = rc().device()->CreateOffscreenPlainSurface(desc.Width,
						desc.Height, intermediateFormat, D3DPOOL_SYSTEMMEM, &psurfSrc[0], NULL);
					if (FAILED(hr))
					{
						guardFailed = true;
						ERROR_MSG("TextureCompressor::copyTexture: failed to create the "
							"scratch source surface %dx%d (hr = 0x%x). Out of memory?\n",
							desc.Width, desc.Height, uint32(hr));
						break;
					}

					hr = rc().device()->CreateOffscreenPlainSurface(desc.Width >> 1,
						desc.Height >> 1, intermediateFormat, D3DPOOL_SYSTEMMEM, &psurfSrc[1], NULL);
					if (FAILED(hr))
					{
						guardFailed = true;
						ERROR_MSG("TextureCompressor::copyTexture: failed to create the "
							"half-size scratch surface %dx%d (hr = 0x%x). Out of memory?\n",
							(desc.Width >> 1), (desc.Height >> 1), uint32(hr));
						break;
					}

					hr = D3DXLoadSurfaceFromSurface(psurfSrc[0], NULL, NULL,
						pOriginalSource, NULL, NULL, D3DX_FILTER_NONE, 0);
					if (FAILED(hr))
					{
						guardFailed = true;
						ERROR_MSG("TextureCompressor::copyTexture: failed to load the "
							"scratch source surface (hr = 0x%x). Out of memory?\n",
							uint32(hr));
						break;
					}
					SAFE_RELEASE(pOriginalSource);

					RECT curRect = { 0, 0, (LONG)desc.Width, (LONG)desc.Height };

					int curSurf = 0;

					// Generate the mipmaps from the lowest known mipmap in the source texture
					for (uint32 level = iLevel; level < numDstMipLevels; level++)
					{
						DX::Surface* psurfDest = NULL;
						hr = pmiptexDest->GetSurfaceLevel(level, &psurfDest);
						if (FAILED(hr))
						{
							guardFailed = true;
							ERROR_MSG("TextureCompressor::copyTexture: failed to get the "
								"destination surface level %d (hr = 0x%x). Out of memory?\n",
								level, uint32(hr));
							break;
						}
						hr = D3DXLoadSurfaceFromSurface(psurfDest, NULL, NULL,
							psurfSrc[curSurf], NULL, &curRect, D3DX_FILTER_NONE, 0);
						if (FAILED(hr))
						{
							guardFailed = true;
							ERROR_MSG("TextureCompressor::copyTexture: failed to generate "
								"destination mip level %d (hr = 0x%x). Out of memory?\n",
								level, uint32(hr));
							SAFE_RELEASE(psurfDest);
							break;
						}

						if (curRect.right >= 2 && curRect.bottom >= 2)
						{
							RECT nextRect = { 0, 0, curRect.right >> 1, curRect.bottom >> 1 };
							int nextSurf = 1 - curSurf;

							hr = D3DXLoadSurfaceFromSurface(psurfSrc[nextSurf], NULL, &nextRect,
								psurfSrc[curSurf], NULL, &curRect, D3DX_FILTER_BOX | D3DX_FILTER_MIRROR, 0);
							if (FAILED(hr))
							{
								guardFailed = true;
								ERROR_MSG("TextureCompressor::copyTexture: failed to "
									"downfilter the scratch surface to mip level %d "
									"(hr = 0x%x). Out of memory?\n",
									level, uint32(hr));
								SAFE_RELEASE(psurfDest);
								break;
							}

							curRect = nextRect;
							curSurf = nextSurf;
						}

						SAFE_RELEASE(psurfDest);
					}

					SAFE_RELEASE(pOriginalSource);
					SAFE_RELEASE(psurfSrc[0]);
					SAFE_RELEASE(psurfSrc[1]);
				} while (false);

				if (guardFailed)
				{
					return false;
				}
			}

			return true;
		}

	} // end of unnamed namespace

	// -----------------------------------------------------------------------------
	// Section: Construction/Destruction
	// -----------------------------------------------------------------------------

	TextureCompressor::TextureCompressor(DX::Texture* srcTexture) :
		srcTexture_(srcTexture),
		srcTextureName_("internal")
	{
	}

	TextureCompressor::TextureCompressor(const BW::StringRef& srcTextureName) :
		srcTexture_(NULL),
		srcTextureName_(srcTextureName.data(), srcTextureName.size())
	{
	}

	/*static*/D3DXIMAGE_FILEFORMAT TextureCompressor::getD3DImageFileFormat(const BW::StringRef& fileName, D3DXIMAGE_FILEFORMAT defaultVal)
	{
		D3DXIMAGE_FILEFORMAT fileFormat = defaultVal;
		BW::StringRef ext = BWResource::getExtension(fileName);
		if (ext.equals_lower("bmp"))
		{
			fileFormat = D3DXIFF_BMP;
		}
		else if (ext.equals_lower("jpg"))
		{
			fileFormat = D3DXIFF_JPG;
		}
		else if (ext.equals_lower("tga"))
		{
			fileFormat = D3DXIFF_TGA;
		}
		else if (ext.equals_lower("png"))
		{
			fileFormat = D3DXIFF_PNG;
		}
		return fileFormat;
	}

	/**
	 *	This method compressed texture into the memory and returns
	 *  result as a binary block
	 *
	 *	@param	TextureDetailLevel	Texture detail level information
	 *
	 *	@return BinaryBlock pointer
	 */
	BinaryPtr TextureCompressor::compressToMemory(
		const SmartPointer< TextureDetailLevel>& dstInfo, const bool bCompressed)
	{
		BW_GUARD;

		MF_ASSERT(dstInfo);
		MF_ASSERT(srcTexture_.pComObject() == NULL);
		MF_ASSERT(srcTextureName_ != "internal");

		D3DFORMAT format;
		if (bCompressed && dstInfo->isCompressed())
		{
			format = dstInfo->formatCompressed();
		}
		else
		{
			format = dstInfo->format();
		}

		// Clamp the conversion policy to what the source image and DX9-class
		// hardware actually allow, before either engine touches the file.
		//  - GUI-class textures (lodMode 0, never streamed) are drawn at
		//    native size by the runtime, so a resample is visible corruption:
		//    honour the source dimensions regardless of what the rule asks.
		//  - A product that keeps non-power-of-two dimensions cannot carry a
		//    mip chain or block compression on DX9 (conditional NPOT support
		//    allows one level, uncompressed only), so fall back to a single
		//    level in an uncompressed format - the same hardware-validity
		//    fallback the nvtt path applies for non multiple-of-4 sizes.
		// This keeps vanilla resources valid: rules that predate NPOT UI art
		// (the demo gui rule asks for DXT5 with resize allowed) no longer
		// produce stretched or uncreatable products.
		D3DFORMAT effFormat = format;
		uint effMipCount = dstInfo->mipCount();
		bool effNoResize = dstInfo->noResize();
		{
			BinaryPtr srcBin = BWResource::instance().rootSection()->readBinary(
				srcTextureName_);
			D3DXIMAGE_INFO srcInfo;
			if (srcBin &&
				SUCCEEDED(D3DXGetImageInfoFromFileInMemory(
					srcBin->data(), (UINT)srcBin->len(), &srcInfo)) &&
				srcInfo.ResourceType == D3DRTYPE_TEXTURE)
			{
				const bool isNPOT =
					((srcInfo.Width & (srcInfo.Width - 1)) != 0) ||
					((srcInfo.Height & (srcInfo.Height - 1)) != 0);

				if (dstInfo->lodMode() == 0 && !dstInfo->streamable())
				{
					// drawn 1:1 by the runtime (GUI elements, thumbnails,
					// tool art): never resample
					effNoResize = true;
				}

				if (effNoResize && isNPOT)
				{
					effMipCount = 1;
					if (isBlockCompressedFormat(effFormat))
					{
						effFormat = D3DFMT_A8R8G8B8;
					}
				}
			}
		}
		// try to use nvtt first if we are not in consumer config
		BinaryPtr bin;
#if ENABLE_NVTT
		if (isFormatNVTTSupported(effFormat))
		{
			bin = compressToMemoryNVTT(srcTextureName_, dstInfo, effFormat,
				effNoResize, effMipCount);
			if (!bin)
			{
				ASSET_MSG("TextureCompressor failed to do nvtt compression for %s, fall back to d3dx\n", srcTextureName_.c_str());
			}
		}
#endif
		if (!bin)
		{
			// fallback to default d3dx conversion
			uint numMips = 0;
			srcTexture_ = loadD3DXTexture(srcTextureName_, dstInfo, &numMips,
				effNoResize, effMipCount);
			if (srcTexture_)
			{
				bin = this->compressToMemory(effFormat, numMips,
					dstInfo->maxExtent());
			}
		}
		return bin;
	}

	//***********************************************************************************************

	/**
	 *	This method converts the given source texture into the given
	 *	texture format, and saves it to the given relative filename.
	 *
	 *	@param	D3DFORMAT	The required destination format
	 *	@param	uint		The number of MIP levels to convert
	 *						(optional, defaults to full mip chain)
	 *
	 *	@return BinaryBlock pointer
	 */

	BinaryPtr TextureCompressor::compressToMemory(D3DFORMAT format, uint numMips,
		uint maxExtent, D3DXIMAGE_FILEFORMAT imgFormat)
	{
		BW_GUARD;

		BinaryPtr bin;
		// default d3dx compression
		ComObjectWrap<DX::Texture> texture = this->compress(format, numMips, maxExtent);

		if (texture)
		{
			SimpleMutexHolder smh(rc().getD3DXCreateMutex());
			ID3DXBuffer* pBuffer = NULL;
			HRESULT hr = D3DXSaveTextureToFileInMemory(&pBuffer,
				imgFormat/*D3DXIFF_DDS*/, texture.pComObject(), NULL);

			if (SUCCEEDED(hr))
			{
				bin = new BinaryBlock(pBuffer->GetBufferPointer(),
					pBuffer->GetBufferSize(), "BinaryBlock/TextureCompressor");

				pBuffer->Release();
			}
		}

		return bin;
	}

	/**
	 *	This method converts the given source texture into the given
	 *	texture format, and saves it to the given relative filename.
	 *
	 *	@param	filename	an absolute path or a resource tree relative filename.
	*	@param	D3DFORMAT	destination texture format
	*	@param	uint		distination number of mip levels
	 *
	 *	@return True if there were no problems.
	 */
	bool TextureCompressor::save(const BW::StringRef& dstFilenameRef,
		D3DFORMAT format, uint numMips, uint maxExtent)
	{
		bool bResult = false;
		D3DXIMAGE_FILEFORMAT fileFormat =
			TextureCompressor::getD3DImageFileFormat(dstFilenameRef, D3DXIFF_DDS);
		BinaryPtr bin = this->compressToMemory(format, numMips, maxExtent, fileFormat);
		if (bin)
		{
			if (BWUtil::isAbsolutePath(dstFilenameRef))
			{
				BW::string dstFilename(dstFilenameRef.data(), dstFilenameRef.size());
				MF_ASSERT(dstFilenameRef.length() <= MAX_PATH);
				FILE* pFile = bw_fopen(dstFilename.c_str(), "wb");

				if (pFile && !ferror(pFile))
				{
					if (bin->len())
					{
						if (fwrite(bin->data(), bin->len(), 1, pFile) == 1)
						{
							bResult = true;
						}
						else
						{
							CRITICAL_MSG("TextureCompressor::save: "
								"Error writing to %s. Disk full?\n",
								dstFilename.c_str());
						}
					}
					fclose(pFile);
				}
			}
			else
			{
				bResult = BWResource::instance().fileSystem()->writeFile(
					dstFilenameRef, bin, true);
			}
		}
		if (!bResult)
		{
			ASSET_MSG("TextureCompressor: Failed to save file %s\n", dstFilenameRef.to_string().c_str());
		}
		return bResult;
	}

	/**
	 *	This method converts the given source texture into the given
	 *	texture format, and saves it to the given relative filename.
	 *
	 *	@param	filename	a resource tree relative filename.
	*	@param	TextureDetailLevelPtr	destination texture info
	 *
	 *	@return True if there were no problems.
	 */
	bool TextureCompressor::save(const BW::StringRef& dstFilename,
		const TextureDetailLevelPtr& dstInfo,
		const bool bCompressed)
	{
		bool bResult = false;
		BinaryPtr bin = this->compressToMemory(dstInfo, bCompressed);
		if (bin)
		{
			bResult = BWResource::instance().fileSystem()->writeFile(
				dstFilename, bin, true);
		}
		if (!bResult)
		{
			ASSET_MSG("TextureCompressor: Failed to save file %s\n", dstFilename.to_string().c_str());
		}
		return bResult;
	}

	/**
	 *	This method converts the given source texture into the given
	 *	texture format, and stows it in the given data section.
	 *
	 *	This method does not save the data section to disk.
	 *
	 *	@param	pSection	a Data Section smart pointer.
	 *	@param	childTag	tag within the given section.
	 *
	 *	@return True if there were no problems.
	 */
	bool TextureCompressor::stow(DataSectionPtr pSection, const BW::StringRef& childTag,
		D3DFORMAT format, uint numMips, uint maxExtent)
	{
		BW_GUARD;

		BinaryPtr binaryBlock = this->compressToMemory(format, numMips, maxExtent);

		//Stick the DDS into a binary section, but don't save the file to disk.
		if (!childTag.empty())
		{
			pSection->delChild(childTag);
			DataSectionPtr textureSection = pSection->openSection(childTag, true);
			textureSection->setParent(pSection);
			textureSection->save();
			textureSection->setParent(NULL);

			if (!pSection->writeBinary(childTag, binaryBlock))
			{
				CRITICAL_MSG("TextureCompressor::stow: error while writing \
							BinSection in \"%s\"\n", childTag.to_string().c_str());
				return false;
			}
		}
		else
		{
			pSection->setBinary(binaryBlock);
		}

		return true;
	}


	/**
	*  This method converts source texture to destination texture.
	*  Destination texture is created in SYSTEMMEMORY pool.
	*
	*	@param D3DFORMAT	format of destination texture.
	*	@param uint			number of mip levels in destination texture.
	*	@returns			converted texture or NULL if operation not succeeded.
	*
	*/
	ComObjectWrap<DX::Texture> TextureCompressor::compress(
		D3DFORMAT dstFormat, uint numMips, uint maxExtent) const
	{
		BW_GUARD;
		//  D3DX conversion only

		MF_ASSERT(srcTexture_);

		// check format and dimensions compatibility
		if (!rc().supportsTextureFormat(dstFormat))
		{
			WARNING_MSG("TextureCompressor: This device does not support "
				"the desired compressed texture format: %d ('%c%c%c%c')\n", dstFormat,
				char(dstFormat >> 24), char(dstFormat >> 16), char(dstFormat >> 8),
				char(dstFormat));
			dstFormat = D3DFMT_A8R8G8B8;
		}

		D3DSURFACE_DESC desc;
		HRESULT hr = srcTexture_->GetLevelDesc(0, &desc);
		if (FAILED(hr))
		{
			ERROR_MSG("TextureCompressor: failed to get the source level "
				"description (hr = 0x%x). Out of memory?\n", uint32(hr));
			return ComObjectWrap<DX::Texture>();
		}

		uint width = desc.Width;
		uint height = desc.Height;
		uint maxd = std::max(width, height);
		if (maxExtent != 0 && maxd > maxExtent)
		{
			float koef = (float)maxd / maxExtent;
			// downscale keeping aspect ratio
			width = std::max<uint>(1, (uint)(width / koef));
			height = std::max<uint>(1, (uint)(height / koef));
		}

		if (((width & 0x3) || (height & 0x3)) &&
			(dstFormat == D3DFMT_DXT1 || dstFormat == D3DFMT_DXT2 ||
				dstFormat == D3DFMT_DXT3 || dstFormat == D3DFMT_DXT4 ||
				dstFormat == D3DFMT_DXT5))
		{
			WARNING_MSG("TextureCompressor: DXT format only support width/height \
				to be multiple of 4. Using uncompressed format instead.\n");
			dstFormat = D3DFMT_A8R8G8B8;
		}

		if (canReuseSource(srcTexture_, dstFormat, numMips, width, height))
		{
			return srcTexture_;
		}

		// create destination texture
		ComObjectWrap<DX::Texture> dstTexture = rc().createTexture(width,
			height, numMips, 0, dstFormat, D3DPOOL_SYSTEMMEM);
		// copy data into it
		if (dstTexture)
		{
			if (!copyTexture(dstTexture, srcTexture_))
			{
				ERROR_MSG("TextureCompressor: texture data copy failed, no "
					"compressed texture was produced (out of memory?).\n");
				return ComObjectWrap<DX::Texture>();
			}
		}
		else
		{
			ERROR_MSG("TextureCompressor: failed to create destination texture \
					 %d x %d %d mips\n", width, height, numMips);
		}
		return dstTexture;

	}

	bool TextureCompressor::compress(ComObjectWrap<DX::Texture>& dstTexture)
	{
		BW_GUARD;
		// d3dx compression only
		return copyTexture(dstTexture, srcTexture_);
	}

} // namespace Moo

BW_END_NAMESPACE

// texture_compressor.cpp
