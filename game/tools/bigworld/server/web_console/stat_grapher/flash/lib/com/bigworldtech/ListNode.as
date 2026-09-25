/**
 * Linked list class
 *
 * Lists are created using ListNode.createList()
 *
 * - Each list has a sentinal (aka head) node which is basically our marker
 *   indicating the start or end of the list.
 * - Lists are circular, so you can iterate in a circle.
 *
 * Usage:
 * - isHead() returns whether we're at the sentinal node and therefore the
 *   start and end of the list (which is circular).
 * - isElement() is the converse of isHead. Returns whether the current node is
 *   an element.
 *
 * Element methods:
 * - insertLeft( val ): inserts a new node with the value "val" to the left of
 *   the current value.
 * - insertRight( val ): inserts a new node with the value "val" to the right of
 *   the current value.
 * - next: is a getter which returns the next node.
 * - prev: is a getter which returns the previous node.
 * - val: is a ListNode attribute which is actually the value assigned to the
 *   node.
 * - remove(): removes the current node from the list. Handles cleanup of
 *   references to neighbour nodes. Can be done during iteration.
 *
 *
 * Head node methods:
 * - start: Reference to first node in list
 * - end: Reference to last node in list
 * - append( val ): inserts a new node at the end of the list
 * - prepend( val ): inserts a new node at the start of the list
 *
 * Example usage:
 *
 * // Create the list
 * // mylist is actually now a reference to the head node
 * var mylist:ListNode = ListNode.createList();
 * mylist.append(5);
 * mylist.prepend(4);
 *
 * for (var node:ListNode = list.start; node.isElement(); node = node.next)
 * {
 *		trace(node.val);
 *		if (node.val == 5)
 *		{
 *			node.remove();
 *		}
 * }
 *
 */

class com.bigworldtech.ListNode
{
	public var val:Object;
	private var __prev:ListNode;
	private var __next:ListNode;

	public static function createList()
	{
		var newList:ListNode = new ListNode();
		newList.val = newList;
		newList.setPrev( newList );
		newList.setNext( newList );

		return newList;
	}

	public function isHead()
	{
		return this.val == this;
	}

	public function isElement()
	{
		return this.val != this;
	}

	public function ListNode( val:Object )
	{
		this.val = val;
		__prev = null;
		__next = null;
	}

	public function setNext( ln:ListNode )
	{
		__next = ln;
	}

	public function setPrev( ln:ListNode )
	{
		__prev = ln;
	}

	public function get next()
	{
		return __next;
	}

	public function getHead()
	{
		var node:ListNode;
		for (node = this; node.isHead() == false; node = node.next)
		{
			// Do nothing
		}

		return node;
	}

	public function get start()
	{
		return getHead().next;
	}

	public function get end()
	{
		return getHead().prev;
	}

	public function get prev()
	{
		return __prev;
	}

	public function insertRight( val:Object )
	{
		var node:ListNode = new ListNode( val );
		node.setPrev( this );
		node.setNext( this.next );

		this.__next.setPrev( node );
		this.setNext( node );
	}

	public function insertLeft( val:Object )
	{
		var node:ListNode = new ListNode( val );
		node.setNext( this );
		node.setPrev( this.prev );

		this.__prev.setNext( node );
		this.setPrev( node );
	}

	public function prepend( val:Object )
	{
		this.getHead().insertRight( val );
	}

	public function append(val:Object)
	{
		this.getHead().insertLeft( val );
	}

	public function toArray()
	{
		var a:Array = new Array();

		for (var node:ListNode = this.start; not node.isHead(); node = node.next)
		{
			a.push( node.val );
		}

		return a;
	}

	public function printList()
	{
		return "[" + this.toArray().join( ", " ) + "]";
	}

	public function isEmpty()
	{
		return start.next == start;
	}

	public function length()
	{
		var len:Number = 0;
		for (var node:ListNode = this.start; not node.isHead();
				node = node.next)
		{
			++len;
		}

		return len;
	}

	public function remove()
	{
		// We shouldn't delete references explicitly since we may still want the
		// val, prev and next references. We'll have to trust the garbage
		// collection to do its job.
		if (this.isHead())
		{
			trace( "Can't remove the head, are you nuts?" );
		}
		else
		{
			this.__prev.setNext( this.__next );
			this.__next.setPrev( this.__prev );
			delete this.val;
		}
	}
}
