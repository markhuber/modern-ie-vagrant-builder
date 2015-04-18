var fs = require('fs');
var page = require('webpage').create();


page.open('https://www.modern.ie/en-us/virtualization-tools', function(status) {

	console.log("Status: " + status);

	var data = page.evaluate(function() {
		return window.vmListJSON;
	});

	var json = JSON.stringify(data, null, 2);

	console.log(fs);

	fs.write("result.json", json, "w");

	phantom.exit();
});

