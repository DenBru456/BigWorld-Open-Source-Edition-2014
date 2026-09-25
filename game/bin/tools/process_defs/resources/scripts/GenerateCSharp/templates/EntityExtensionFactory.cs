using System;
using System.Collections.Generic;
using System.Text;

{% if generatedNamespace != "BW" -%}
using BW;{%- endif %}

namespace {{ generatedNamespace }}
{
/// <summary>
/// This class is responisible for entity extension creation off
/// entity type id.
/// </summary>
public class EntityExtensionFactory : EntityExtensionFactoryBase
{
	#region Accessors
	/// <summary>
	/// This method retrieves an extension from the given entity that 
	/// corresponds to this factory.
	/// </summary>
	/// <param name="entity">Entity to get the extension from.</param>
	public IEntityExtension getForEntity( Entity entity )
	{
		return entity.extensionInSlot( this.slot );
	}
	#endregion Accessors

	#region Public virtual extension creators
{%- for entity in entityDescriptions %}		
	public virtual IEntityExtension createForEntity( {{ entity.name }} entity )
	{
		return null;
	}
{% endfor %}
	#endregion Public virtual extension creators
}


} // namespace {{ generatedNamespace }}
