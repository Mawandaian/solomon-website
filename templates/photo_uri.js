// JavaScript Document
"use strict";

		const compressor = new Compress()
		const upload = document.getElementById('file1')
		const upload2 = document.getElementById('file2')
		const preview = document.getElementById('preview')
		const preview2 = document.getElementById('preview2')

		upload.addEventListener('change', function (evt){
			const files = [...evt.target.files]
			compressor.compress(files, {
				size: 4,
				quality: .75
			}).then((results) => {
				console.log(results)
				const output = results[0]
				const file = Compress.convertBase64ToFile(output.data, output.ext)
				console.log(file)
				preview.src = output.prefix + output.data
				document.getElementById('photo_data_uri').value = output.prefix + output.data
			})
		}, false)
		
		
		
		upload2.addEventListener('change', function (evt){
			const files = [...evt.target.files]
			compressor.compress(files, {
				size: 4,
				quality: .75
			}).then((results) => {
				console.log(results)
				const output = results[0]
				const file = Compress.convertBase64ToFile(output.data, output.ext)
				console.log(file)
				preview2.src = output.prefix + output.data
				document.getElementById('photo_data_uri2').value = output.prefix + output.data
			})
		}, false)
		
		