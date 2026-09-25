using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Text;

using BW;
using BW.Types;
{% if generatedNamespace != "BW" -%}
using {{ generatedNamespace }};{% endif %}

namespace {{ generatedNamespace }}
{

/// <summary>
/// This class is the base class for the {{ entity.name }} entity type.
/// </summary>
public sealed class {{ className }} : Entity
{
	/// <summary>
	/// Constructor
	/// </summary>
	public {{ className }}( ConnectionWithModel connection ) :
		base(connection)
	{
{%- if hasCellMailbox %}
		cell_ = new CellMB.{{ entity.name }}(this);{% endif %}
{%- if hasBaseMailbox %}
		base_ = new BaseMB.{{ entity.name }}(this);{% endif %}
	}

	/// <summary>
	/// Override form Entity.
	/// </summary>
	public override string entityTypeName { get { return "{{ entity.name }}"; } }

	#region Public property accessors
{%- for property in entity.clientProperties %}
	public {{ property.type|ctype }} {{ property.name }} { get { return {{ property.name }}_; } }
{%- endfor %}
	#endregion Public property accessors

	#region Public mailbox accessors
{%- if hasCellMailbox %}
	public CellMB.{{ entity.name }} cellMB { get { return cell_; }	} {% endif %}
{%- if hasBaseMailbox %}
	public BaseMB.{{ entity.name }} baseMB { get { return base_; } } {% endif %}
	#endregion Public mailbox accessors

	#region Entity overrides
	/// <summary>
	/// This method initialises the base {{ entity.name }} player from the stream. At
	/// this point, the player does not have a cell yet, so only BASE_AND_CLIENT 
	/// properties are streamed here.
	/// </summary>
	protected override bool initBasePlayerFromStream( BinaryIStream stream )
	{
{%- for property in entity.baseToClientProperties %}
		stream.read( {% if property.type|cshouldRef %}ref {% endif %}{{ property.name }}_ );{% endfor %}
		return !stream.error;
	}
	
	/// <summary>
	/// This method initialises the cell {{ entity.name }} player from stream. 
	/// At this point, the OWN_CLIENT, OTHER_CLIENT cell properties are streamed.	
	/// </summary>
	protected override bool initCellPlayerFromStream( BinaryIStream stream )
	{
{%- for property in entity.cellToClientProperties %}
		stream.read( {% if property.type|cshouldRef %}ref {% endif %}{{ property.name }}_ );{% endfor %}
		return !stream.error;
	}

	/// <summary>
	/// This method creates an entity extension for the given factory.
	/// </summary>
	protected override void createExtension( EntityExtensionFactoryBase factory )
	{
		EntityExtensionFactory fcast = factory as EntityExtensionFactory;
		if (fcast == null)
		{
			return;
		}
		IEntityExtension ext = fcast.createForEntity( this );
		if (ext != null)
		{
			if (factory.slot >= 0)
			{
				this.setExtension( ext, factory.slot );
			}
		}

	}
	
	protected override void onProperty( int propertyID, BinaryIStream stream,
		bool shouldCallback )
	{
		//Log.TRACE_MSG( "{{ className }}.onProperty: " + propertyID );

		switch (propertyID)
		{
{%- for property in entity.clientProperties %}
			case {{ property.clientServerFullIndex }}:
			{
				stream.read( {% if property.type|cshouldRef %}ref {% endif %}{{ property.name }}_ );
				if (shouldCallback)
				{
					{#-this.set_{{ property.name }}();#}
					this.callPropertyChange( "{{ property.name }}" );
				}
				break;
			}
{% endfor %}
			default: break;
		}
	}
	
	protected override void onMethod( int methodID, BinaryIStream stream )
	{
		//Log.TRACE_MSG( "{{ entity.name }}.onMethod: " + methodID );

		switch( methodID )
		{
{%- for method in entity.clientMethods %}
		case {{ method.exposedIndex }}: // {{ method.name }}
		{ {% for arg in method.args %}
			{{ arg.1|ctype }} {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif -%}
			{%- if not arg.1|cshouldRef %} = new {{arg.1|ctype}}(
				{%- if arg.1|carraySize > 0 %} {{ arg.1|carraySize }} {% endif %})
				{%- else %} = default( {{ arg.1|ctype }} ){%- endif %};
			stream.read( {% if arg.1|cshouldRef %}ref {% endif %}{% if arg.0 %}{{ arg.0 }}
				{%- else %}arg{{ loop.index0 }}{% endif %} );
			{%- endfor %}

			//Log.TRACE_MSG( "Calling {{ entity.name }}.{{ method.name }}" );

			this.{{ method.name }}( {% for arg in method.args %}{% if not loop.first %},
				{% endif %}{% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% endfor %} );
			break;
		}
{% endfor %}
		default:
			Log.ERROR_MSG( "{{ className }}.onMethod: Unknown method " +
				methodID );
			break;
		}
	}

	/// <summary>
	/// This method is called when a nested property change has been sent from
	/// the server.
	/// </summary>
	protected override void onNestedProperty( BinaryIStream stream, bool isSlice, bool shouldCallback )
	{
		if (isSlice)
		{
			this.onSlicedPropertyChange( stream, shouldCallback );
		}
		else
		{
			this.onSinglePropertyChange( stream, shouldCallback );
		}
	}

	/// <summary>
	/// This method is called when the network layer needs to know how big 
	/// a given method message is.
	/// </summary>
	protected override int getMethodStreamSize( int methodID )
	{
		switch (methodID)
		{
	{% for method in entity.clientMethods %}
		case {{ method.exposedIndex }}: // {{ method.name }}
			return {{ method.streamSize }};
	{% endfor %}
		default:
			Log.ERROR_MSG( "{{ className }}.getMethodStreamSize: Unknown method " +
					methodID );
			break;
		}

		return 0;
	}

	/// <summary>
	/// This method is called when the network layer needs to know how big 
	/// a given property message is.
	/// </summary>
	protected override int getPropertyStreamSize( int propertyID )
	{
		switch (propertyID)
		{
	{% for property in entity.clientProperties %}
		case {{ property.clientServerFullIndex }}: // {{ property.name }}
			return {{ property.streamSize }};
	{%endfor%}
		default:
			Log.ERROR_MSG( "{{ className }}.getPropertyStreamSize: Unknown property " +
					propertyID );
			break;
		}

		return 0;
	}
	#endregion Entity overrides


	#region Protected extension management callbacks
	protected override void onExtensionAdded( int slot, IEntityExtension ext )
	{
		refreshCallableExtensions();
	}
	protected override void onExtensionRemoved( int slot, IEntityExtension ext )
	{
		refreshCallableExtensions();
	}

	protected override void onExtensionsCleared()
	{
		callableExtensionsNum_ = 0;
	}
	
	private void refreshCallableExtensions()
	{
		callableExtensionsNum_ = 0;
		foreach (IEntityExtension ext in extensions_)
		{
			if (ext is {{ extensionName }})
			{
				callableExtensions_[ callableExtensionsNum_++ ] = ext as {{ extensionName }};
			}
		}
	}
	
	private {{ extensionName }}[] callableExtensions_ = new {{ extensionName }}[MAX_EXTENSIONS];
	private int callableExtensionsNum_ = 0;
	#endregion Protected extension management callbacks
{% if entity.clientMethods %}
	#region Public virtual methods.
	// The derived class {{ entity.name }} needs to implement these methods.
{%- for method in entity.clientMethods %}
	private {{ method|methodDeclaration }}
	{
		for (int i = 0; i < callableExtensionsNum_; i++)
		{
			{{ extensionName }} ext = callableExtensions_[i];
			ext.{{ method.name }}( {% for arg in method.args %}{% if not loop.first %},
				{% endif %}{% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% endfor %} );
		}
	}
{% endfor %}
	#endregion Public virtual methods.
{% endif %}
	#region Property setter callback
	private void callPropertyChange( string propertyName )
	{
		for (int i = 0; i < callableExtensionsNum_; i++)
		{
			{{ extensionName }} ext = callableExtensions_[i];
			ext.onPropertyChange( propertyName );
		}
	}
	#endregion

	#region Private methods
	private void onSinglePropertyChange( BinaryIStream stream, bool shouldCallback )
	{
		var change = new NestedPropertyChange( NestedPropertyChange.ChangeType.SINGLE, stream );

		const int NUM_PROPERTIES = {{ entity.clientProperties | count }};
		int propertyID = (int)change.readNextIndex( NUM_PROPERTIES );

		if (change.isFinished)
		{
			this.onProperty( propertyID, stream, false );
			return;
		}

		switch (propertyID)
		{
	{%- for property in entity.clientProperties %}
	{%- if not property.isConst %}
			case {{ property.clientServerFullIndex }}: // {{ property.name }}
			{
				object obj = {{ property.name }}_;
				if (!change.apply( ref obj ))
				{
					Log.ERROR_MSG( "Failed to set %s from stream\n" +
							"{{ entity.name }}.{{ property.name }}" );
					return;
				}

				if (shouldCallback)
				{
					{#- this.setNested_{{ property.name }}( change.path ); #}
					this.callPropertyChange( "{{ property.name }}" );
				}

				break;
			}
	{%- endif %}
	{%- endfor %}
			default:
				Log.ERROR_MSG( "Invalid property change on {{ entity.name }}, index = " +
					propertyID );
				break;
		}
	}
	
	private void onSlicedPropertyChange( BinaryIStream stream, bool shouldCallback )
	{
		var change = new NestedPropertyChange( NestedPropertyChange.ChangeType.SLICE, stream );

		const int NUM_PROPERTIES = {{ entity.clientProperties | count }};
		int propertyID = (int)change.readNextIndex( NUM_PROPERTIES );

		// Entity-level is not slice-able.
		Debug.Assert( !change.isFinished );

		switch (propertyID)
		{
	{%- for property in entity.clientProperties %}
	{%- if not property.isConst %}
			case {{ property.clientServerFullIndex }}: // {{ property.name }}
			{
				object obj = {{ property.name }}_;
				if (!change.apply( ref obj ))
				{
					Log.ERROR_MSG( "Failed to set slice for %s from stream " +
						"{{ entity.name }}.{{ property.name }}" );
					return;
				}

				if (shouldCallback)
				{
					{#- NestedPropertyChange.Slice oldSlice = change.oldSlice;
					this.setSlice_{{ property.name }}( change.path, oldSlice.first, oldSlice.second ); #}
					this.callPropertyChange( "{{ property.name }}" );
				}

				break;
			}
	{%- endif %}
	{%- endfor %}
			default:
				Log.ERROR_MSG( "Invalid sliced property change on {{ entity.name }}, index = " +
					propertyID );
				break;
		}
	}
	#endregion Private methods

	#region Private members
{% if hasCellMailbox %}	private CellMB.{{ entity.name }} cell_;{% endif %}
{% if hasBaseMailbox %}	private BaseMB.{{ entity.name }} base_;{% endif %}

{% for property in entity.clientProperties %}
	private {{ property.type|ctype }} {{ property.name -}}_
		{%- if not property.type|cshouldRef %} = new {{ property.type|ctype -}}
		({% if property.type|carraySize  > 0 %} {{ property.type|carraySize }} {% endif %})
	{%- endif -%};
{%- endfor %}
	#endregion Private members
};

} // namespace {{ generatedNamespace }}
