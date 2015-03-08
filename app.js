var fs = require('fs');
var url = require('url');
var downloader = require('./downloader.js');


var data = JSON.parse(fs.readFileSync('result.json', 'utf8'));

var linuxOsList = data.osList[0];
var browsers = linuxOsList.softwareList[0].browsers;
var file;

for (var i = 0; i <= browsers.length - 1; i++) {
	file = browsers[i].files[1];
	console.log('---------------------------------------------------');
	console.log('MD5: ' + file.md5);
	console.log('Name: ' + file.name);
	console.log('URL: ' + file.url);
	console.log('---------------------------------------------------');

	downloader.downloadFile(file);
	//downloader.getRemoteMd5(file, function(md5) { console.log('MD5 Result: ' + md5); });
	//downloader.getFileMd5(file.name, function(md5) { console.log('Local MD5 Result: ' + md5)});
	break;
};


