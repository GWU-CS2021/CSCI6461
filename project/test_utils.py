def load_file( file_path="paragraph.txt"):
    with open(file_path, "r+") as p_reader:
        tmp_string = p_reader.read()
        for char in tmp_string:
            print(char,ord(char))


load_file()