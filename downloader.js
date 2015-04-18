//var wget = require('wget');
var progressBar = require('progress');
var http = require('https');
var md5 = require('MD5');
var exec = require('child_process').execSync;
var fork = require('child_process').fork;
var spawn = require('child_process').spawn;
var fs = require('fs');

var downloader = function () {

	var DOWNLOAD_DIR = "./downloads";

	function downloadFile(fileInfo) {
		
		var bar = new progressBar(fileInfo.name + ' [:bar] :percent :etas', { total: 100000 });

		var wget = spawn('wget ' + fileInfo.url + ' -o ' + DOWNLOAD_DIR + '/' + fileInfo.name);
			
		wget.stdout.on('data', function (data) {
		  process.stdout.write(data);
		});

		wget.stderr.on('data', function (data) {
		  process.stderr.write(data);
		});

		wget.on('exit', function (code) {
		  console.log('child process exited with code ' + code);
		});

//		var download = wget.download(fileInfo.url, DOWNLOAD_DIR+'/'+ fileInfo.name, {});
		
//		download.on('error', function(err) {
//		    console.log(err);
//		});
//		download.on('end', function(output) {
//		    console.log(output);
//		});
//		download.on('progress', function(progress) {
//		    if ((Math.floor(progress*1000) % 10) == 0) {
//		    	bar.tick();
//		    }
//		});
		
	}

	function getFileMd5(filename, callback){
		
		exec('md5 -q ' + DOWNLOAD_DIR + '/' + filename, function( error, stdout, stderr){
			callback(stdout);
		});

		//console.log('filename: ' + filename);
		//fs.readFile(DOWNLOAD_DIR+'/'+filename, function(err, buf) {
		//	if(err){
		//		console.log(err);
		//	}
		//	callback(md5(buf));
		//	
		//})
	}

	function getRemoteMd5(path, callback) {
		var str = '';
		
		http.request(path.md5, function(resp) {
			
			resp.on('data', function(chunk) {
				str += chunk;
			});

			resp.on('end', function() {
				callback(str);
			});
		}).end();
	}

	return {
		downloadFile: downloadFile,
		getRemoteMd5: getRemoteMd5,
		getFileMd5: getFileMd5
	}
}

module.exports = downloader();