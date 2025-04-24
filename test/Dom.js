
// this is a wrapper class to create ui elements in javascript
// it is a simple class that wraps around the html element class
export class element {
	static _to_element(elem) {
		return new element(null).elem(elem);
	}

	// creates a new html element
	// if tagName is null, the element is not initialized
	// else the element is initialized with the tagName
	constructor(tagName='div') {
		if (tagName == null) 
			this._elem = null;
		else
			this._elem = document.createElement(tagName);
	} 
	// sets the inner element to elem
	elem(elem) {
		this._elem = elem;
		return this;
	}
	// gets the inner element
	get_elem() {
		return this._elem;
	}

	// sets the id of the element
	id(id) {
		this._elem.id = id;
		return this;
	}
	// gets the id of the element
	get_id() {
		return this._elem.id;
	}

	// sets the text of the element
	text(text) {
		this._elem.innerText = text;
		return this;
	}
	// gets the text of the element
	get_text() {
		return this._elem.innerText;
	}

	// sets the value of the element
	value(value) {
		this._elem.value = value;
		return this;
	}
	// gets the value of the element
	get_value() {
		return this._elem.value;
	}

	// clears the inner html of the element
	clear() {
		this._elem.innerHTML = '';
		return this;
	}

	// adds an event listener to the element
	event(event, func) {
		this._elem.addEventListener(event, func);
		return this;
	}

	// appends a child element to the element
	// the child element must be an instance of this class
	append_child(child) {
		this._elem.appendChild(child.get_elem());
		return this;
	}
	pop_child() {
		this._elem.removeChild(this._elem.lastChild);
		return this;
	}
	// appends a list of children to the element
	// the children must be instances of this class
	append_children(children) {
		for (let child of children) {
			this.append_child(child);
		}
		return this;
	}

	// removes a child element from the element
	// the child element must be an instance of this class
	remove_child(child) {
		this._elem.removeChild(child.get_elem());
		return this;
	}

	// adds a class to the element
	add_class(className) {
		this._elem.classList.add(className);
		return this;
	}

	// adds a list of classes to the element
	add_classes(classNames) {
		for (let className of classNames) {
			this.add_class(className);
		}
		return this;
	}

	// gets the first element by query from _elem
	get_element_by_query(query) {
		return element._to_element(this._elem.querySelector(query));
	}

	// gets all elements by query from _elem
	get_elements_by_query(query) {
		return [...this._elem.querySelectorAll(query)]
			.map(elem => element._to_element(elem));
	}

	// gets all elements by class from _elem
	get_elements_by_class(className) {
		return [...this._elem.getElementsByClassName(className)]
			.map(elem => element._to_element(elem));
	}

	// gets all elements by tag from _elem
	get_elements_by_tag(tagName) {
		return [...this._elem.getElementsByTagName(tagName)]
			.map(elem => element._to_element(elem));
	}

	// gets all elements by name from _elem
	get_elements_by_name(name) {
		return [...this._elem.geteleme(name)]
			.map(elem => element._to_element(elem));
	}
}

// a helper function for new element(tagName)
export function make_element(tagName='div') {
	return new element(tagName);
}

let _to_element = element._to_element;

// gets the body element
export function get_body() {
	return _to_element(document.body);
}

// gets an element by id from the document
export function get_element_by_id(id) {
	return _to_element(document.getElementById(id));
}

// gets the first element by query from the document
export function get_element_by_query(query) {
	return _to_element(document.querySelector(query));
}


// gets all elements by query from the document
export function get_elements_by_query(query) {
	return [...document.querySelectorAll(query)]
		.map(elem => _to_element(elem));
}

// gets all elements by class from the document
export function get_elements_by_class(className) {
	return [...document.getElementsByClassName(className)]
		.map(elem => _to_element(elem));
}

// gets all elements by tag from the document
export function get_elements_by_tag(tagName) {
	return [...document.getElementsByTagName(tagName)]
		.map(elem => _to_element(elem));
}

// gets all elements by name from the document
export function get_elements_by_name(name) {
	return [...document.getElementsByName(name)]
		.map(elem => _to_element(elem));
}

export function on_page_load(func) {
	window.onload = func;
}
	