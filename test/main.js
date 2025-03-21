import {on_page_load, get_body} from './Dom.js';
import { request } from "./Request.js";
async function main() {
	console.log('main');

	fetch('http://localhost:8000')
	.then(response => response.text())
	.then(text => {
		document.open();  // Clear the current document
		document.write(text);  // Write the new HTML response
		document.close();  // Close and render
	});
}


on_page_load(main);