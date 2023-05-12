"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const zipstream_1 = require("./zipstream");
exports.handler = async (event, context) => {
    let bucket = 'laravel-env-management-686642117901';
    let uris = event.destination_uris;
    let files = { "files": [] };
    let x = 0;
    for (let uri of uris) {
        files["files"][x] = {
            "uri": uri,
            "filename": ".env",
            "type": "file"
        };
        x += 1;
    }
    for (const file of files["files"]) {
        let y = file['uri'];
        let z = y.concat(file['filename']);
        let destinationKey = z.concat('.zip');
        await new Promise(async (resolve, reject) => {
            let zipStream = (0, zipstream_1.streamTo)(bucket, destinationKey, resolve);
            zipStream.on("error", reject);
            let archive = (0, zipstream_1.archiver)("zip");
            archive.on("error", err => {
                throw new Error(err.toString());
            });
            archive.pipe(zipStream);
            if (file["type"] == "file") {
                archive.append((0, zipstream_1.getStream)(bucket, z), {
                    name: file["filename"]
                });
            }
            else if (file["type"] == "url") {
                archive.append((0, zipstream_1.request)(file['uri']).toString(), { name: file["filename"] });
            }
            archive.finalize();
        }).catch(err => {
            throw new Error(err);
        });
    }
    return {
        statusCode: 200
    };
};
