from fuzzywuzzy import fuzz
import numpy as np
import pandas as pd

# pembuatan dataframe dummy
df_dummy = pd.DataFrame({
    "nama": ["Suyatno", "Ayu Prahara", "Prahara Ayu", "P. Ayu", "P. Ayu","Sandra Dewi", "Dew Sandra", "Pramita Adin", "P. Adin", "Niko", "nico"],
    "ibu_kandung":["Bunga", "Diva Pertiwi", "Pertiwi Diva","P. Diva", "Dita", "Lina Sandra", "Sandra Lina", "Amelia Assyfa", "Assyfa A", "Roselina Sulina", "Mawar Sri"],
    "alamat":["Tanah Abang", "Blok m", "Blok m", "m Block", "Block m", "Antapani", "Antapani", "Ciputra", "Ciputra", "Ciputra", "bSD"],
    "dob":["1970/01/01", "1985/12/05", "1985/12/05", "1985/12/05", "1999/04/18", "1989/03/15", "1989/03/15", "2000/09/20", "2000/09/20", "1992/02/02", "1998/10/19"]
    })


# function ini menerima argumen berupa dataframe
def fuzzy_credit_score(df):

    # Pembuatan array dan membuat lower seluruh stringnya
    nama = np.char.lower(list(df["nama"]))
    ibu_kandung = np.char.lower(list(df["ibu_kandung"]))
    alamat = np.char.lower(list(df["alamat"]))
    dob = np.char.lower(list(df["dob"]))
    dob_baru = np.array([])

    # transform data untuk meningkatkan performa fuzzy 
    for i in range(len(dob)):
        dob_baru = np.append(dob_baru, dob[i][2:].replace("/",""))
    dob = dob_baru

    # perhitungan fuzzy scoring
    hasil = [] # array untuk menyimpan hasil score keseluruhan 
    for i in range(len(nama)):

        sementara = np.array([]) # array untuk menampung score yang membandingkan satu orang terhadap yang lainnya.
        for j in range(len(nama)):
            score_nama = fuzz.ratio(nama[i], nama[j]) # score fuzzy menggunakan ratio dari levensthein (urutan karakter dari dua buah string)
            score_nama_2 = fuzz.token_sort_ratio(nama[i], nama[j]) # split perkata sebelum diperiksa ratio menggunakan levenshtein
            if score_nama_2> score_nama:
                score_nama = score_nama_2

            score_ibu = fuzz.ratio(ibu_kandung[i], ibu_kandung[j]) # score fuzzy menggunakan ratio dari levensthein (urutan karakter dari dua buah string)
            score_ibu_2 = fuzz.token_sort_ratio(ibu_kandung[i], ibu_kandung[j]) # split perkata sebelum diperiksa ratio menggunakan levenshtein
            if score_ibu_2> score_ibu:
                score_ibu = score_ibu_2

            score_alamat = fuzz.ratio(alamat[i],alamat[j]) # score fuzzy menggunakan ratio dari levensthein (urutan karakter dari dua buah string)
            score_alamat_2 = fuzz.token_sort_ratio(alamat[i],alamat[j]) # split perkata sebelum diperiksa ratio menggunakan levenshtein
            if score_alamat_2>score_alamat:
                score_alamat = score_alamat_2

            score_dob = fuzz.ratio(dob[i],dob[j]) # score fuzzy menggunakan ratio dari levensthein (urutan karakter dari dua buah string)

            score = score_nama*0.5 + score_ibu*0.3 + score_alamat*0.1 + score_dob*0.1
            if score_nama <= 20: # batas bawah seseorang dianggap memiliki nama yang sama
                score = 0
            if score_ibu <= 20: # batas bawah seseorang dianggap memiliki nama ibu yang sama
                score = 0

            # kondisi dimana nama orang tersebut sama atau mirip,
            # namun orang tersebut orang yang berbeda (diperiksa dengan melihat score nama ibu dan dob).
            # Berhasil mengatasi kasus p. ayu pada data dummy yang memiliki nama sama dan nama ibu mirip.
            if score_nama >60 and score_ibu <= 60 and score_dob <= 30: 
                score = 0
            
            sementara = np.append(sementara, score)
        hasil.append(sementara)

    # Block ini digunakan untuk mengatasi masalah jika terdapat dua orang dengan nama yang sama (Agar data tidak tereplace)
    # contoh kasus p. ayu (nama ibu : diva) dan p. ayu (nama ibu : dita)
    # hasilnya akan menjadi p. ayu dan p. ayu(2)
    nama_edit = []
    for i in range(len(nama)):
        nomor = 1
        name = nama[i]
        while name in nama_edit:
            nomor+=1
            name = name+"("+str(nomor)+")"
        nama_edit.append(name)

    # Blok untuk memutuskan apakah dua orang yang dibandingkan merupakan orang yang sama atau berbeda
    list_nama_sama = []
    for i in range(len(hasil)):
        sementara = np.array([])
        for j in range(len(hasil[i])):
            if i != j:
                if hasil[i][j] >60: # threshold
                    sementara= np.append(sementara,nama_edit[j])
        list_nama_sama.append(sementara)

    df_final = pd.DataFrame({"orang sama":list_nama_sama}, index=nama_edit)
    df_final = df_final.to_dict()['orang sama']
    return df_final

# print(fuzzy_credit_score(df_dummy)["ayu prahara"]) # contoh pemanggilan fungsi untuk meliat orang yang sama dengan ayu prahara
    