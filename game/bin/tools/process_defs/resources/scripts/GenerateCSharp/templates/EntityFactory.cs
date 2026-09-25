using System;
using System.Collections.Generic;
using System.Text;

{% if generatedNamespace != "BW" -%}
using BW;{%- endif %}

namespace {{ generatedNamespace }}
{

/// <summary>
/// This class is responisible for entity creation off
/// entity type id
/// </summary>
class EntityFactory : IEntityFactory
{
	#region Constructors
	public EntityFactory()
	{
{%- for entity in entityDescriptions %}		
		creators_[ {{ entity.clientIndex}} ] =
			( ConnectionWithModel conn ) => 
			{ return new {{ entity.name }}{% if shouldGenerateView %}View{% endif %}( conn ); };
{% endfor %}
	}
	#endregion Constructors

	/// <summary>
	/// This method creates an entity
	/// </summary>
	/// <param name="entityTypeID">Entity Type ID</param>
	/// <param name="connection">ConnectionWithModel instance for the new entity</param>
	/// <returns></returns>
	public Entity create( Int16 entityTypeID, ConnectionWithModel connection )
	{
		DCreator creator;
		if (!creators_.TryGetValue( entityTypeID, out creator ))
		{
			return null;
		}
		return creator( connection );
	}

	#region Private helpers
	delegate Entity DCreator( ConnectionWithModel connection );
	Dictionary<Int16, DCreator> creators_ = new Dictionary<Int16, DCreator>();
	#endregion Private helpers
}


} // namespace {{ generatedNamespace }}
