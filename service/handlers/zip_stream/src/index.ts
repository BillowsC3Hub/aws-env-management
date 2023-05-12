import { Context } from 'aws-lambda';
import { DestinationUris } from './DestinationUris';
import { ZipStreamFiles } from './ZipStreamFiles';
import { streamTo, archiver, getStream, request } from "./zipstream";
import { logger, metrics, tracer } from "./utils/utilities";

// Need to check if theres any uris. Function succeeds even when empty 
exports.handler = async (event: DestinationUris, context: Context) => {
    let bucket = 'laravel-env-management-686642117901' //process.env.S3_BUCKET;
    let uris = event.destination_uris;

    let files: ZipStreamFiles = {"files": []};
    let x = 0
    for (let uri of uris) {
      files["files"][x] = { // Info in this object could be dynamic 
        "uri" : uri,
        "filename" : ".env",
        "type" : "file"
      }
      x += 1;
    }

    for (const file of files["files"]) {
      let y = file['uri'];
      let z = y.concat(file['filename']);
      let destinationKey = z.concat('.zip');

      await new Promise(async (resolve, reject) => {
        let zipStream = streamTo(bucket, destinationKey, resolve);
        zipStream.on("error", reject);
    
        let archive = archiver("zip");
        archive.on("error", err => {
          throw new Error(err.toString());
        });
        archive.pipe(zipStream);

        if (file["type"] == "file") {
          archive.append(getStream(bucket, z), {
            name: file["filename"]
          });
        } else if (file["type"] == "url") {
          archive.append(request(file['uri']).toString(), { name: file["filename"] });
        }
        archive.finalize();
      }).catch(err => {
        throw new Error(err);
      });
    }
      return {
          statusCode: 200
          // body: { final_destination: destinationKey } // What can we add here to return 
        }

        // Need to figure out failed status code 500? 
  };