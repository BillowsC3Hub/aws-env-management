"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.request = exports.getStream = exports.archiver = exports.streamTo = void 0;
const aws_sdk_1 = __importDefault(require("aws-sdk"));
const stream_1 = __importDefault(require("stream"));
const archiver_1 = __importDefault(require("archiver"));
exports.archiver = archiver_1.default;
const request_1 = __importDefault(require("request"));
exports.request = request_1.default;
const awsOptions = {
    httpOptions: {
        timeout: 300000
    }
};
const s3 = new aws_sdk_1.default.S3(awsOptions);
const streamTo = (bucket, key, resolve) => {
    var passthrough = new stream_1.default.PassThrough();
    s3.upload({
        Bucket: bucket,
        Key: key,
        Body: passthrough,
        ContentType: "application/zip",
        ServerSideEncryption: "AES256"
    }, (err, data) => {
        if (err)
            throw err;
        console.log("Zip uploaded");
        resolve();
    }).on("httpUploadProgress", (progress) => {
        console.log(progress);
    });
    return passthrough;
};
exports.streamTo = streamTo;
const getStream = (bucket, key) => {
    let streamCreated = false;
    const passThroughStream = new stream_1.default.PassThrough();
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
exports.getStream = getStream;
