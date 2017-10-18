import requests

BASE_PATH = "C:/Users/Lukasz/PycharmProjects/bot-drama-quotes/"

with open("urls.txt") as urls_file:
    for line in urls_file:
        line = line.strip()
        filename = line.split("/")[-1]
        destination_path = BASE_PATH + "dramas/" + filename
        extension = filename.split(".")[-1]
        title = "".join(filename.split(".")[:-1])
        r = requests.get(line)
        if r.status_code != 200:
            print(f"Nie znaleziono pliku {filename}, być może plik na stronie "
                  f"https://wolnelektury.pl/katalog/lektura/{title}/ ma inną nazwę.")
        else:
            with open(destination_path, "wb") as drama_file:
                drama_file.write(r.content)
