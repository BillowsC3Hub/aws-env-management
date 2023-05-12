// Lambda S3 Zipper
// http://amiantos.net/zip-multiple-files-on-aws-s3/
//
// Accepts a bundle of data in the format...
// {
//     "bucket": "your-bucket",
//     "destination_key": "zips/test.zip",
//     "files": [
//         {
//             "uri": "...", (options: S3 file key or URL)
//             "filename": "...", (filename of file inside zip)
//             "type": "..." (options: [file, url])
//         }
//     ]
// }
// Saves zip file at "destination_key" location

"use strict";


import AWS from "aws-sdk";
import Stream, { Pipe, Readable } from 'stream';
import archiver from "archiver";
import request from "request";

const awsOptions = {
  //region: "us-east-1",
  httpOptions: {
    timeout: 300000 // Matching Lambda function timeout
  }
};

const s3 = new AWS.S3(awsOptions);

const streamTo = (bucket: string, key: string, resolve: any) => {
  var passthrough = new Stream.PassThrough();
  s3.upload(
    {
      Bucket: bucket,
      Key: key,
      Body: passthrough,
      ContentType: "application/zip",
      ServerSideEncryption: "AES256"
    },
    (err, data) => {
      if (err) throw err;
      console.log("Zip uploaded");
      resolve();
    }
  ).on("httpUploadProgress", (progress) => {
    console.log(progress);
  });
  return passthrough;
};

// Kudos to this person on GitHub for this getStream solution
// https://github.com/aws/aws-sdk-js/issues/2087#issuecomment-474722151
const getStream = (bucket: string, key: string) => {
  let streamCreated = false;
  const passThroughStream = new Stream.PassThrough();

  passThroughStream.on("newListener", event => {
    if (!streamCreated && event == "data") {
      const s3Stream = s3
        .getObject({ Bucket: bucket, Key: key })
        .createReadStream();
      s3Stream
        .on("error", err => passThroughStream.emit("error", err))
        .pipe(passThroughStream);

      streamCreated = true;
    }
  });

  return passThroughStream;
};

export {
  streamTo,
  archiver, 
  getStream, 
  request
};
