#include "wtl.hpp"
#include "main_window.hpp"
#include "jit_compiler.hpp"
#include "task_store.hpp"
#include "message_loop.hpp"

#include "asset_pipeline/compiler/asset_compiler_options.hpp"

#include "resmgr/bwresource.hpp"
#include "resmgr/dataresource.hpp"
#include "resmgr/multi_file_system.hpp"

#include "cstdmf/command_line.hpp"
#include "cstdmf/debug_message_file_logger.hpp"

BW_BEGIN_NAMESPACE
DECLARE_WATCHER_DATA( NULL )
DECLARE_COPY_STACK_INFO( false )
BW_END_NAMESPACE

namespace
{
	bool init()
	{
		WTL::AtlInitCommonControls(ICC_COOL_CLASSES | ICC_BAR_CLASSES);

		// Initialise the file systems
		if (!BW::BWResource::init( BW::BWResource::appDirectory(), false ))
		{
			return false;
		}
		BW::BWResource::instance().enableModificationMonitor( true ); 

		return true;
	}

	void fini()
	{
		// Cleanup the file systems
		BW::BWResource::fini();

		::CoUninitialize();
	}
}



#define JIT_COMPILER_LOG_FILE_ENABLED 1

// Starts a log file named <exe name>.log in the exe directory and
// routes engine debug messages into it. Disable at runtime with
// the "disableLogFile" command line parameter.
void initLogFile(const BW::CommandLine& commandLine)
{
#if JIT_COMPILER_LOG_FILE_ENABLED
	static BW::DebugMessageFileLogger logFile;

	if (commandLine.hasParam("disableLog"))
	{
		logFile.enable(false);
		return;
	}

	wchar_t exePath[MAX_PATH] = { 0 };
	::GetModuleFileNameW(NULL, exePath, MAX_PATH);
	BW::string logFileName = BW::bw_wtoutf8(exePath);

	size_t slashPos = logFileName.find_last_of('\\');
	size_t dotPos = logFileName.find_last_of('.');
	if (dotPos != BW::string::npos &&
		(slashPos == BW::string::npos || dotPos > slashPos))
	{
		logFileName.erase(dotPos);
	}
	logFileName += ".log";

	logFile.config(logFileName,
		BW::DebugMessageFileLogger::SERVERITY_ALL,
		"",
		BW::DebugMessageFileLogger::SOURCE_ALL,
		BW::DebugMessageFileLogger::OVERWRITE,
		true);
#endif // JIT_COMPILER_LOG_FILE_ENABLED
}



#pragma comment(linker,"\"/manifestdependency:type='win32' \
name='Microsoft.Windows.Common-Controls' version='6.0.0.0' \
processorArchitecture='*' publicKeyToken='6595b64144ccf1df' language='*'\"")


int WINAPI WinMain( HINSTANCE instance, HINSTANCE prevInstance, LPSTR commandLine, int showCmd )
{
	BW_SYSTEMSTAGE_MAIN();
#ifdef ENABLE_MEMTRACKER
	MemTracker::instance().setCrashOnLeak( true );
#endif

	int exitCode = 1;

	BW::CommandLine logCommandLine(
		BW::bw_wtoutf8(GetCommandLineW()).c_str());
	initLogFile(logCommandLine);

	if (init())
	{
		BW::AssetCompilerOptions options;
		options.parseCommandLine( BW::bw_wtoutf8( GetCommandLineW() ) );

		BW::TaskStore store;
		BW::MainMessageLoop messageLoop;
		BW::JITCompiler jitCompiler(store);
		BW::MainWindow mainWindow(store, messageLoop, jitCompiler, jitCompiler);
		options.apply(jitCompiler);
		jitCompiler.initPlugins();
		jitCompiler.initCompiler();

		if (mainWindow.init())
		{
			// Spawn another thread to do the disk scanning for the JIT Compiler
			auto scanningThreadFunc = [](void * arg)
			{
				BW::JITCompiler * jitCompiler = static_cast< BW::JITCompiler *>( arg );
				jitCompiler->scanningThreadMain();
			};
			BW::SimpleThread jitScanningThread(scanningThreadFunc, &jitCompiler, "JITCompiler Scanning Thread");

			auto managingThreadFunc = [](void * arg)
			{
				BW::JITCompiler * jitCompiler = static_cast< BW::JITCompiler *>( arg );
				jitCompiler->managingThreadMain();
			};
			BW::SimpleThread jitManagingThread(managingThreadFunc, &jitCompiler, "JITCompiler Process Thread");

			exitCode = messageLoop.run();

			jitCompiler.stop();
		}

		mainWindow.fini();

		jitCompiler.finiCompiler();
		jitCompiler.finiPlugins();
	}

	fini();

	return exitCode;
}
