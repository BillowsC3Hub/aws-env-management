export interface ZipStreamFiles {
    files: File[];
}

export interface File {
    uri:      string;
    filename: string;
    type:     string;
}


// is there a place I should be putting these files. I.E schemas in python 