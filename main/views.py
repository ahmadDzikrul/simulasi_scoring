from django.shortcuts import render
import pandas as pd
import csv
# from fuzzy_credit_scoring import fuzzy_credit_score

from fuzzywuzzy import fuzz
import numpy as np

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
    nama = np.char.lower(list(df["nama_debitur"]))
    ibu_kandung = np.char.lower(list(df["nama_ibu_kandung"]))
    alamat = np.char.lower(list(df["alamat_ktp"]))
    dob = np.char.lower(list(df["tanggal_lahir"]))

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
            name = nama[i]+"("+str(nomor)+")"
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
    


def home(request):
    return render(request, "main/home_start.html")


def home2(request):
    return render(request, "main/home2.html")

# fungsi ini nanti akan jadi fungsi pemanggilan SQL dari postgre
def read_data():
    string = '''
    1,14/02/1976,Wahyu Simanjuntak,Mira Kurnia Sari,Bulevar Hijau Blok F2 No. 18A,12/12/2010,26/09/2024,12/12/2010,166,333162476.4,2958562,2611735,346827,0,0,0,0,0,142,24,667536474,69365382.4,26/09/2022,0,0,1,64101745,KPR,6
    2,12/06/1984,Argono Daru Tarihoran S.Sos,Defita Rossa Sandriana Naseer,TANAH KUSIR,12/02/2020,26/01/2024,12/02/2020,48,85000000,2452679,1930999,52168,0,0,0,0,0,32,16,34893448,36824447,26/09/2022,0,0,1,34893463,KTA,17
    3,23/02/1980,Iriana Ade Usada,Kayla Putri Legawa,DANAU LAUT TAWAR G 3E NO 30,10/06/2013,26/06/2029,10/06/2013,192,300000000,2434314,1617185,817129,0,0,0,0,0,111,81,161808658,163425843,26/09/2022,0,0,1,161808735,KPR,6
    4,16/01/1988,Janet Nuraini,Aaliyah Mai,CITRA 2 EXT BLOK B1-7/ 17,28/11/2014,26/11/2029,28/11/2014,180,460000000,3881741,2515238,1366503,0,0,0,0,0,94,86,270785325,273300563,26/09/2022,0,0,1,256367242,KPR,6
    5,11/11/1981,Kambali Tampubolon,Abigail Garza,JL.INDRA,28/03/2013,26/03/2033,28/03/2013,240,429000000,3073489,1631330,1442159,0,0,0,0,0,114,126,286800537,288431867,26/09/2022,0,0,1,286800484,KPR,6
    6,21/10/1982,Karimah Keisha Suryatmi,Abigail Mejia,JLN TALAUT 4 RT 003 RW 002,16/03/2017,26/02/2037,16/03/2017,240,765000000,5480698,2301130,3179568,0,0,0,0,0,67,173,633612423,635913553,26/09/2022,0,0,1,618188417,KPR,6
    7,21/11/1982,Karsana Caturangga Budiman S.Pt,Abigail Vang,LINGKUNGAN PANDANSARI,28/03/2016,26/03/2036,28/03/2016,240,557200000,5170980,753976,4417004,67,67,37,36,5,75,165,377846361,377846361,18/08/2022,2315117,13197823,2,405122516,KPR,14
    8,24/01/1986,Maida Nuraini,Alice Soto,Jl Meranti I,01/04/2021,26/02/2024,01/04/2021,36,79632311,2612920,2267097,345823,5,5,6,6,5,17,19,43842653,46109750,27/09/2022,2284100,328820,2,,JOINT FINANCING,9
    9,11/09/1984,Kasiran Uwais,Addison Do,JL FLAMBOYAN NO,29/07/2021,26/07/2026,29/07/2021,60,50000000,1269671,630648,639023,0,0,0,0,0,14,46,41970884,42601532,26/09/2022,0,0,1,41970876,KTA,18
    10,27/12/1981,Kasusra Mandala,Addison Mehta,JL BAKTI NO 508,11/07/2022,26/06/2027,11/07/2022,60,70000000,1777540,74953,1028010,0,0,0,0,0,3,57,67784477,68534007,26/09/2022,0,0,1,67784477,KTA,18
    11,06/06/1984,Keisha Natalia Nurdiyanti,Addison Perez,JL G BAMBAMPUANG,19/04/2021,26/03/2035,19/04/2021,168,448718610,3954270,1862049,2092221,0,0,0,0,0,18,150,416582195,418444244,26/09/2022,0,0,1,416582209,KPR,6
    12,19/01/1982,Langgeng Gunarto,Addison Roberts,BTN PAGUTAN REGENCY NO. B3,15/07/2021,26/06/2025,15/07/2021,48,85000000,2452679,1520280,932399,0,0,0,0,0,15,33,64296145,65816425,26/09/2022,0,0,1,64296153,KTA,17
    13,28/09/1985,Mala Pudjiastuti S.Psi,Alice Thompson,JL PERMATA II,29/01/2019,26/01/2023,29/01/2019,48,60000000,1731303,1613714,117589,0,0,0,0,0,44,4,6686696,8300410,26/09/2022,0,0,1,6686722,KTA,17
    14,24/01/1978,Malik Luis Wibowo,Alice Tran,Jl MR Latuharhary No 58,11/11/2021,10/10/2024,11/11/2021,35,63753915,2077849,1710971,366878,0,0,0,0,0,10,25,47206131,48917102,14/09/2022,0,0,1,46860137,JOINT FINANCING,9
    15,28/06/1985,Oman Prasasta,Giovanna Redenta Therezia Renesse,JL TIANG BENDERA III,06/07/2022,26/05/2027,06/07/2022,60,175000000,3366408,2533385,833023,0,0,0,0,0,4,56,164071186,166604571,26/09/2022,0,0,1,164071184,KPM,6
    16,28/02/1985,Luhung Prabu Megantara S.T.,Alice Mehta,PONDOK GEDE PERMAI,24/08/2021,26/07/2023,24/08/2021,24,15000000,734447,63487,99577,0,0,0,0,0,14,10,6833391,7468261,26/09/2022,0,0,1,6833401,KTA,16
    17,05/12/1981,Aurora Titin Safitri,Shafa Fitrisya Kharisma Damayanti,KEBON JAHE,01/10/2020,26/09/2023,01/10/2020,36,30000000,1054711,887878,166833,0,0,0,0,0,24,12,11624612,12512490,26/09/2022,0,0,1,11624612,KTA,16
    18,06/09/1981,Pia Ika Safitri,Pavita Maheswari Iswandaru Putri,JL.KABEL NO.92 KP.PITARA,17/05/2013,26/04/2033,17/05/2013,240,566500000,4058582,2143475,1915107,0,0,0,0,0,113,127,380877916,383021391,26/09/2022,0,0,1,380877923,KPR,6
    19,12/09/1984,Aisyah Farida,Fasha Hira Azzahra,CENGKARENG RESIDENCE,25/07/2022,26/06/2025,25/07/2022,36,100000000,3515703,2240954,1274749,0,0,0,0,0,3,33,93365208,95606162,26/09/2022,0,0,1,93365207,KTA,16
    20,05/02/1976,Anita Mardhiyah,Azzahra Putri Erwita,JL. KLP CENGKIR RAYA CL I/4,07/03/2013,26/02/2031,07/03/2013,216,1338000000,10144212,6099300,4044912,0,0,0,0,0,115,101,802883010,808982310,27/09/2022,0,0,1,802883038,KPR,6
    21,09/07/1971,Artawan Pranowo,Anjani Elmawati,PERUM WAHANA PONDOK GEDE BLOK D7 NO18,27/11/2014,26/11/2026,27/11/2014,144,528000000,5220949,4041620,1170622,0,0,0,0,0,94,50,230082878,234124498,26/09/2022,0,0,1,271819314,KPR,6
    22,05/05/1982,Ayu Yuliarti,Ica Febrianti Rustiningsih,TELUK GONG JL. C NO.76,12/10/2012,26/09/2032,12/10/2012,240,680000000,4871731,2664341,2207390,0,0,0,0,0,120,120,438813681,441478022,26/09/2022,0,0,1,420330360,KPR,6
    23,30/06/1987,Azalea Riyanti,Natasya Hanska Susanti,JL TANAH TINGGI V,16/02/2021,26/01/2023,16/02/2021,24,36000000,1762672,1649719,112953,0,0,0,0,0,20,4,6821788,8471507,26/09/2022,0,0,1,6821788,KTA,16
    24,03/04/1978,Mahmud Candrakanta Lazuardi S.Pt,Alice Roberts,Jl Sarean No 19,10/01/2022,03/12/2024,10/01/2022,35,44333573,1444907,1172137,27277,0,0,0,0,0,8,27,35197189,35197189,31/08/2022,0,0,1,34920185,JOINT FINANCING,9
    25,09/04/1969,Banawi Hidayat,Amanda Kalila,JL. GEDUNG PINANG NO.139,27/09/2017,26/09/2024,27/09/2017,84,1150000000,16799838,14830424,1969414,0,0,0,0,0,60,24,379052463,393882887,26/09/2022,0,0,1,377515387,KPR,6
    26,01/07/1971,Cager Teguh Wijaya S.Pt,Karyn Gabriella,JL. MANUNGGAL XVII NO 47,06/09/2013,26/08/2026,06/09/2013,156,350000000,3236532,2547469,689063,0,0,0,0,0,109,47,135265105,137812574,26/09/2022,0,0,1,134542859,KPR,6
    27,15/12/1976,Calista Fujiati S.T.,Salsabila Syafa Marwa Laksmana,JAPOS GRAHA LESTARI,23/08/2022,26/07/2023,23/08/2022,12,50000000,4166667,4166667,0,0,0,0,0,0,2,10,41666666,45833333,26/09/2022,0,0,1,41666668,KTA,0
    28,05/07/1981,Cayadi Umay Hardiansyah S.Pd,Ninda Putri Ayu Lestari,JL. Q 1 BLOK GG NO. 5,09/03/2012,26/02/2027,09/03/2012,180,550000000,4641213,3545392,1095821,0,0,0,0,0,127,53,215618859,219164251,26/09/2022,0,0,1,206301865,KPR,6
    29,20/08/1984,Darijan Kadir Waluyo,Gwyneth Caroline Imbar,JL BUDI MULIA,21/02/2022,26/01/2024,21/02/2022,24,30000000,1468893,1172737,296156,0,0,0,0,0,8,16,21038982,22211719,26/09/2022,0,0,1,21038979,KTA,16
    30,12/09/1980,Dina Mulyani,Elsie Felice Bennitha Padi Gunadi,JL BAUNG NO26,03/11/2020,26/10/2023,03/11/2020,36,85000000,2988348,2482553,505795,0,0,0,0,0,23,13,35452048,37934601,26/09/2022,0,0,1,35452055,KTA,16
    31,16/01/1982,Edi Tarihoran,Aisha Sabina Prameswari,JL MANDAR XII,23/10/2018,26/09/2023,23/10/2018,60,80000000,2031474,1673989,357485,0,0,0,0,0,48,12,22158333,23832322,26/09/2022,0,0,1,22158314,KTA,18
    32,05/08/1975,Ellis Ella Usada S.H.,Rana Mahira Althaf,JL SMA 48 PINANG RANTI NO 8,26/07/2013,26/07/2028,26/07/2013,180,500000000,4219284,2961068,1258216,0,0,0,0,0,110,70,248682172,251643240,26/09/2022,0,0,1,246282958,KPR,6
    33,24/10/1970,Estiawan Suryono,Nameira Hamidah Fahmi,KP PISANGAN,02/12/2019,26/11/2023,02/12/2019,48,50000000,1442752,1168293,274459,0,0,0,0,0,34,14,18205302,19373595,26/09/2022,0,0,1,18205296,KTA,17
    34,19/05/1983,Faizah Widiastuti,Kevindra Akiko Meliala,JL SUTOYO,27/12/2019,26/12/2024,27/12/2019,60,100000000,2539343,1673679,865664,0,0,0,0,0,33,27,56037235,57710914,26/09/2022,0,0,1,56037242,KTA,18
    35,20/02/1979,Galur Hidayat,Nayla Shabira Putri,RAWA BUAYA NO.43,17/09/2019,26/08/2023,17/09/2019,48,80000000,2308403,1949843,35856,0,0,0,0,0,37,11,23360298,25310141,26/09/2022,0,0,1,23360271,KTA,17
    36,14/10/1982,Harjasa Lazuardi,Azzahra Mayraina Rahmatputri,JL.DATU M.AKIP NO.78,24/07/2017,26/06/2037,24/07/2017,240,935000000,6698630,2756938,3941692,0,0,0,0,0,63,177,785581542,788338480,26/09/2022,0,0,1,766098512,KPR,6
    37,15/04/1978,Hasna Riyanti S.E.I,Cahaya Candida,JL KESADARAN IV,02/12/2021,26/11/2022,02/12/2021,12,30000000,2500000,2500000,0,0,0,0,0,0,10,2,5000000,7500000,26/09/2022,0,0,1,5000000,KTA,0
    38,30/04/1985,Ihsan Harjasa Prabowo,Satra Farhana,PERUM METLAND MENTENG BLOK D1,13/10/2017,26/09/2037,13/10/2017,240,1100000000,7880742,3195288,4685454,0,0,0,0,0,60,180,933895555,937090843,26/09/2022,0,0,1,910416511,KPR,6
    39,23/02/1980,Iriana Ade Usada,Kayla Putri Legawa,JL DANAU LAUT TAWAR G3 E-30,15/07/2021,26/06/2036,15/07/2021,180,700000000,5906998,2581075,3325923,0,0,0,0,0,15,165,662603560,665184635,26/09/2022,0,0,1,662603568,KTA,6
    40,08/09/1968,Dian Aryani,Jessenia sarah Aurelia,GG RUSA VI,06/07/2022,26/06/2023,06/07/2022,12,17000000,1416667,1416667,0,0,0,0,0,0,3,9,12749999,14166666,26/09/2022,0,0,1,12750002,KTA,0
    41,18/09/1980,Lanjar Gunarto,Adeline Huang,Perum PIP Blok E No 68,01/10/2021,30/08/2024,01/10/2021,35,53023118,1728114,1433660,294454,1,1,2,2,1,11,24,37826929,39260589,15/09/2022,1444412,283702,2,37559952,JOINT FINANCING,9
    42,25/06/1976,Ajimin Aditya Pangestu,Illeana Kezia Beatrix,PERUM VILLA KRISTA,19/03/2019,26/02/2024,19/03/2019,60,30000000,637411,548966,88445,0,0,0,0,0,43,17,10064478,10613444,26/09/2022,0,0,1,10064454,KTA,10
    43,25/06/1975,Ajimin Aditya Pangestu,Illeana Kezia Beatrix,DAWUNG TENGAH,26/12/2010,26/07/2025,26/12/2010,175,117916395,1012631,850432,162199,0,0,0,0,0,141,34,31589465,32439897,26/09/2022,0,0,1,29722181,KPR,6
    44,20/04/1985,Latika Puspita,Adeline Thao,JL HIBRIDA,19/01/2022,26/12/2025,19/01/2022,48,100000000,2885504,1643798,1241706,0,0,0,0,0,9,39,86006061,87649859,26/09/2022,0,0,1,86006058,KTA,17
    45,02/04/1983,Lidya Sudiati,Adeline Yang,Lingkungan Burujul,11/01/2022,10/12/2022,11/01/2022,11,34052011,3236676,3141369,95307,0,0,0,0,0,8,3,9566173,12707542,12/09/2022,0,0,1,9533823,JOINT FINANCING,9
    46,23/11/1992,Lili Alika Purwanti,Alice Lopez,Jl SMA 13 Lr. Petai 6,08/06/2022,07/05/2025,08/06/2022,35,30671096,999623,781177,218446,0,0,0,0,0,3,32,28344967,29126144,12/09/2022,0,0,1,28083982,JOINT FINANCING,9
    47,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,07/01/2015,20/12/2023,07/01/2015,108,60000000,612591,510172,102419,0,0,0,0,0,93,15,8395837,8906009,20/09/2022,0,0,1,7756069,KTA,13.8
    48,01/07/1985,Mitra Prasasta,Caroline Santos,PCP I JL TANGKUBAN PERAHU BLOK J NO 28,04/03/2016,26/02/2031,04/03/2016,180,278419209,2349461,1412636,936825,0,0,0,0,0,79,101,185952317,187364953,26/09/2022,0,0,1,174107676,KPR,6
    49,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,03/12/2014,20/12/2023,03/12/2014,109,80000000,794098,661333,132765,0,0,0,0,0,94,15,10883489,11544822,20/09/2022,0,0,1,10054128,KTA,13.8
    50,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,03/12/2014,20/12/2023,03/12/2014,109,80000000,794098,661333,132765,0,0,0,0,0,94,15,10883489,11544822,20/09/2022,0,0,1,10054128,KTA,13.8
    51,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,03/12/2014,20/12/2023,03/12/2014,109,40000000,397051,330668,66383,0,0,0,0,0,94,15,5441750,5772418,20/09/2022,0,0,1,5027078,KTA,13.8
    52,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,03/12/2014,20/12/2023,03/12/2014,109,40000000,397051,330668,66383,0,0,0,0,0,94,15,5441750,5772418,20/09/2022,0,0,1,5027078,KTA,13.8
    53,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,06/01/2015,20/12/2023,06/01/2015,108,80000000,816787,680228,136559,0,0,0,0,0,93,15,11194430,11874658,20/09/2022,0,0,1,10341423,KTA,13.8
    54,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,06/01/2015,20/12/2023,06/01/2015,108,80000000,816787,680228,136559,0,0,0,0,0,93,15,11194430,11874658,20/09/2022,0,0,1,10341423,KTA,13.8
    55,24/09/1970,Melinda Namaga S.Pt,Amelia Salazar,DESA MARGA SAKTI,06/01/2015,20/12/2023,06/01/2015,108,80000000,816787,680228,136559,0,0,0,0,0,93,15,11194430,11874658,20/09/2022,0,0,1,10341423,KTA,13.8
    56,05/08/1968,Marsito Winarno,Alice Xiong,JALUR X DUSUN IV,07/11/2014,05/11/2022,07/11/2014,96,100000000,1680726,1627266,5346,0,0,0,0,0,94,2,3307534,4934800,05/09/2022,0,0,1,3306372,KTA,13
    57,05/08/1968,Marsito Winarno,Alice Xiong,JALUR X DUSUN IV,07/11/2014,05/11/2022,07/11/2014,96,100000000,1680726,1627266,5346,0,0,0,0,0,94,2,3307534,4934800,05/09/2022,0,0,1,3306372,KTA,13
    58,29/08/1972,Satya Budiman,Isabella Scott,Dore,25/08/2022,12/06/2024,25/08/2022,22,24091867,1192005,1011316,108413,0,0,0,0,0,1,21,23080551,24091867,21/09/2022,0,0,1,22859434,JOINT FINANCING,9
    59,09/05/1962,Satya Sihombing M.M.,Isabella Soto,Jl Kesuma No 20,22/12/2021,21/11/2024,22/12/2021,35,29135272,949568,776085,173483,0,0,0,0,0,9,26,22354915,23131000,08/09/2022,0,0,1,22185008,JOINT FINANCING,9
    60,25/03/1992,Shania Rika Pratiwi,Lily Carter,Kmp Bunisari,28/04/2022,28/03/2025,28/04/2022,35,54898600,1789239,1408726,380513,3,3,4,4,0,4,31,49326305,50735031,01/09/2022,1419292,369947,2,48885247,JOINT FINANCING,9
    61,12/02/1968,Warji Uda Pradana,Melody Grant,Jl Re Martadinata,17/03/2021,17/02/2023,17/03/2021,24,116791849,5593016,5347807,245209,0,0,15,0,0,18,6,27346714,38002518,19/09/2022,0,0,1,,JOINT FINANCING,9
    62,20/03/1985,M. Athaa Sudibyo,Samantha Chavez,Dsn Cinenggang,04/08/2021,02/07/2023,04/08/2021,23,44266315,2102582,1936678,165904,0,0,0,0,0,13,10,20183896,22120574,06/09/2022,0,0,1,20089509,JOINT FINANCING,9
    63,31/12/1969,Dimas Prasetyo Utomo,Samantha Foster,Jl Batang Tebo,27/07/2020,27/05/2023,27/07/2020,35,35906364,1221145,1141726,79419,0,0,0,0,0,26,9,9447518,10589244,28/09/2022,0,0,1,,JOINT FINANCING,9
    64,12/01/1984,Ravier Gavino,Stella Lai,Kp Sudi,10/08/2022,09/07/2024,10/08/2022,23,51962625,2468145,2094013,374132,0,0,0,0,0,2,21,47790187,49884200,12/09/2022,0,0,1,47350746,JOINT FINANCING,9
    65,03/11/1983,Nico Anggoro Putro,Stella Wu,Kp Cireundeu,24/08/2022,22/07/2024,24/08/2022,23,27531288,1307694,1101209,199602,0,0,0,0,0,1,22,26430079,27531288,23/09/2022,0,0,1,26176396,JOINT FINANCING,9
    66,23/03/1983,Mursita Damanik,Emily Lau,Lingkungan Talun Kidul,08/02/2022,07/01/2024,08/02/2022,23,124465622,5911925,5206705,70522,0,0,0,0,0,7,16,88822614,94029319,05/09/2022,0,0,1,88186575,JOINT FINANCING,9
    67,02/09/1991,Tiara Wijayanti S.E.,Lily Henderson,Luwung,16/11/2021,15/10/2023,16/11/2021,23,36948360,1754990,1580680,17431,0,0,0,0,0,10,13,21660695,23241375,07/09/2022,0,0,1,21532362,JOINT FINANCING,9
    68,25/10/1980,M. Aragani Abi Akbari,Mila Allen,Jl Mayjen Katamso,09/03/2021,03/02/2023,09/03/2021,23,28730898,1404534,1317123,60393,0,0,0,0,0,18,5,6735285,8052408,05/09/2022,0,0,1,,JOINT FINANCING,9
    69,30/09/1968,M. Raihan Adliputra,Valentina Davis,Golf Komp Permata Golf II Blk F12,12/11/2021,11/10/2023,12/11/2021,23,81297152,3861489,3477956,383533,0,0,0,0,0,10,13,47659839,51137795,09/09/2022,0,0,1,47377469,JOINT FINANCING,9
    70,03/04/1981,Aditya Arya Pratama,Valentina Moua,Lingkungan Kampo Tolo,18/08/2022,16/07/2025,18/08/2022,35,61639138,2008924,1546630,446884,0,0,0,0,0,1,34,60092508,61639138,19/09/2022,0,0,1,59507409,JOINT FINANCING,9
    71,18/12/1979,Ariansah,Victoria Johnson,Dusun Embung,24/11/2021,23/10/2023,24/11/2021,23,67552062,3208619,2868417,340202,8,8,9,9,8,9,14,42491811,45360228,19/09/2022,2889930,318689,2,42222503,JOINT FINANCING,9
    72,25/01/1967,Nabila Icha Lestari,Emma Brooks,Jambu Tonang,19/07/2022,18/06/2023,19/07/2022,11,99686360,9475282,8793092,68219,0,0,0,0,0,2,9,82165634,90958726,13/09/2022,0,0,1,81478428,JOINT FINANCING,9
    73,05/05/1977,Fikri Baihaqy Noor,Mila Hong,Dusun Gembolo,26/04/2022,25/03/2025,26/04/2022,35,46305572,1509177,1188224,320953,6,6,0,0,0,4,31,41605485,41605485,30/08/2022,1197136,312041,2,41233461,JOINT FINANCING,9
    74,08/09/2000,M. Fauzan Rabbani,Natalia Diaz,Jl Budi Mulia No. 47 Rt 009 Rw 012 Kel.,25/01/2022,21/12/2024,25/01/2022,35,20450961,676076,535895,140181,0,0,0,0,0,8,27,16285780,16821675,20/09/2022,0,0,1,16157452,JOINT FINANCING,10
    75,23/12/1983,Warta Pranowo,Melody Ho,Jl NIH Doko,16/09/2022,13/08/2025,16/09/2022,35,130833550,4264088,0,0,0,0,0,0,0,0,35,130833550,,16/09/2022,0,0,1,129525214,JOINT FINANCING,9
    76,10/03/1979,Wisnu Mandala,Melody Valdez,Tegalsari,19/12/2019,19/12/2023,19/12/2019,48,76694068,2088207,1730441,249115,43,43,13,13,12,31,17,31484886,31484886,30/08/2022,3499914,459198,2,,JOINT FINANCING,9
    77,25/02/1963,Yance Riyanti,Mia Cheng,Jl Subyadinata No 442,29/07/2022,28/06/2026,29/07/2022,47,106373515,2693944,1924691,769253,0,0,0,0,0,3,44,100642317,102567008,27/09/2022,0,0,1,99694684,JOINT FINANCING,9
    78,28/02/1979,Nova Hasanah,Emma Cao,Jl Majapahit III Blok 16 No 15,23/09/2022,22/08/2026,23/09/2022,47,102359200,2592280,0,0,0,0,0,0,0,0,47,102359200,,23/09/2022,0,0,1,101335608,JOINT FINANCING,9
    79,12/12/1976,Nova Raina Yulianti,Emma Perry,Jl Farel Pasaribu No.138,20/04/2022,19/03/2025,20/04/2022,35,101650000,3312947,2627954,684993,0,0,0,0,0,5,30,88704408,91332362,19/09/2022,0,0,1,87934902,JOINT FINANCING,9
    80,06/06/1978,Omar Januar,Eva Alvarado,Kp Gembrong,09/08/2022,06/07/2024,09/08/2022,23,115086800,5466446,4603295,805608,0,0,0,0,0,1,22,110483505,115086800,06/09/2022,0,0,1,109423057,JOINT FINANCING,9
    81,26/07/1975,Lucky Aldi Akbar,Natalia Owens,Jl Sunan Drajat,23/09/2022,22/08/2025,23/09/2022,35,42584911,1387915,0,0,0,0,0,0,0,0,35,42584911,,23/09/2022,0,0,1,42159062,JOINT FINANCING,9
    82,16/07/1982,Yulia Yulianti,Mia Herrera,Jl Khm Kasim,20/05/2022,19/04/2025,20/05/2022,35,132307181,4312116,3395070,917046,0,0,0,0,0,4,31,118877792,122272862,20/09/2022,0,0,1,117814829,JOINT FINANCING,9
    83,31/03/1974,Yunita Tiara Laksita,Mia Lam,Jl Rengganis,17/12/2021,16/11/2024,17/12/2021,35,85807800,2796622,2251786,544836,46,46,16,16,0,7,28,70392977,70392977,30/08/2022,4554365,1038879,2,69820025,JOINT FINANCING,9
    84,12/07/1968,Joddi Mursin Putra Elman,Mia Wu,Jl Dermaga Gg. Pelita,17/03/2022,16/02/2025,17/03/2022,35,37061314,1207891,965331,24256,0,0,0,0,15,6,29,31376057,32341388,27/09/2022,0,0,1,31112260,JOINT FINANCING,9
    85,11/11/1995,Oskar Hakim,Eva Coleman,Jl Dr Sutomo No 05,11/10/2021,04/09/2024,11/10/2021,35,44166153,1439450,1194181,245269,0,0,0,0,0,11,24,31508336,32702517,05/09/2022,0,0,1,31285945,JOINT FINANCING,9
    86,09/02/1983,Tina Pertiwi,Lily Nguyen,Jl Wr Supratman I 8 Lingk Kepatihan,29/08/2022,26/07/2024,29/08/2022,23,18817897,893821,752687,131725,0,0,0,0,0,1,22,18065210,18817897,27/09/2022,0,0,1,17891815,JOINT FINANCING,9
    87,17/06/1979,Tira Nurdiyanti,Lily Pena,Nglencong I,18/01/2022,17/12/2023,18/01/2022,23,51686516,2455030,2178391,276639,0,0,0,0,0,8,15,34706744,36885135,16/09/2022,0,0,1,34472476,JOINT FINANCING,9
    88,29/07/1986,Helmy Mustafa Amir,Samantha Adams,Jorong Kota,30/06/2022,29/05/2025,30/06/2022,35,51830320,1689238,1320091,369147,0,0,0,0,0,3,32,47899454,49219545,22/09/2022,0,0,1,47458421,JOINT FINANCING,9
    89,12/01/1988,Azril Alfaza Pramana Putra,Samantha Aguilar,Dadapan,27/11/2020,27/10/2022,27/11/2020,24,40012397,1922979,1866355,56624,35,35,36,35,35,20,4,5683476,7549831,06/09/2022,3774809,71149,2,,JOINT FINANCING,9
    90,27/12/1983,Panca Saputra,Eva Estrada,Jl Sawit Perum Elivar Damai,26/08/2022,25/07/2026,26/08/2022,47,86118064,2180968,1535083,645885,0,0,0,0,0,1,46,84582981,86118064,23/09/2022,0,0,1,83753570,JOINT FINANCING,9
    91,07/01/1989,Paris Andriani,Eva Figueroa,Dusun II,19/08/2022,18/07/2024,19/08/2022,23,29255725,1389602,1170184,219418,0,0,0,0,0,1,22,28085541,29255725,13/09/2022,0,0,1,27815969,JOINT FINANCING,9
    92,24/08/1972,Radika Niyaga Saptono,Eva Garcia,Jl Beringin,15/07/2022,14/06/2025,15/07/2022,35,72328874,2357321,1828466,528855,0,0,0,0,0,2,33,68685554,70514020,19/09/2022,0,0,1,68034933,JOINT FINANCING,9
    93,01/12/1981,Ratih Shakila Usada S.Gz,Eva Jenkins,Kp Kaumkidul,27/10/2020,27/08/2023,27/10/2020,35,50487111,1711031,1564290,146741,0,0,0,5,0,23,12,18001198,19565488,30/09/2022,0,0,1,,JOINT FINANCING,9
    94,01/12/1981,Ratih Shakila Usada S.Gz,Eva Jenkins,Kp Kaumkidul,24/09/2021,23/08/2023,24/09/2021,23,38356250,1821863,1665617,156246,0,0,0,0,0,12,11,19167221,20832838,26/09/2022,0,0,1,19069591,JOINT FINANCING,9
    95,04/03/1984,Titin Laksita,Lyla Stewart,Dsn Citelun,13/01/2020,13/01/2023,13/01/2020,37,60028891,1994106,1906680,87426,18,18,19,19,18,31,6,9750063,11656743,13/09/2022,1920981,73125,2,,JOINT FINANCING,9
    96,20/06/1976,Victoria Winarsih,Lyla Yoon,Jl Ikan Mas III/16,18/03/2020,18/01/2023,18/03/2020,35,84289539,2880155,2774537,105618,0,0,0,0,0,30,5,11307809,14082346,19/09/2022,0,0,1,,JOINT FINANCING,9
    97,20/06/1976,Victoria Winarsih,Lyla Yoon,Jl Ikan Mas III/16,22/09/2022,21/08/2026,22/09/2022,47,98686969,2499279,1759127,715481,0,0,0,0,0,1,46,96927842,,23/09/2022,0,0,1,95977378,JOINT FINANCING,9
    98,29/12/1972,Dimas Satria Yudha,Samantha Barnes,Tarogong Tengah,18/11/2021,17/10/2024,18/11/2021,35,75477500,2459940,2010518,449422,14,14,15,15,0,9,26,57912379,59922897,19/09/2022,2025597,434343,2,57472225,JOINT FINANCING,9
    99,11/09/1979,Sabrina Widiastuti,Isabella Bailey,Cawan,16/03/2022,15/02/2024,16/03/2022,23,32331561,1535699,1342441,193258,0,0,0,0,0,6,17,24425339,25767780,14/09/2022,0,0,1,24240429,JOINT FINANCING,9
    100,28/05/1972,Salsabila Mayasari S.T.,Isabella Bui,Dsn Bantardawa,03/06/2022,02/05/2024,03/06/2022,23,38164196,1812740,1549492,263248,0,0,0,0,0,3,20,33550238,35099730,06/09/2022,0,0,1,33255299,JOINT FINANCING,9
    '''
    kolom ='''No,tanggal_lahir,nama_debitur,nama_ibu_kandung,alamat_ktp,tanggal awal,tanggal selesai,angsuran_pertama_tanggal,jangka_waktu (bulan),loan_amount,angsuran_perbulan,pokok,bunga,dpd (day past due)(hari tunggakan),tunggakan_m,tunggakan_m1,tunggakan_m2,tunggakan_m3,angsuran_ke,sisa_tenor,baki_debet,baki_debet_bulan_lalu,tanggal_bayar_terakhir,tunggakan_pokok,tunggakan_bunga,kolektibilitas; 1 dan 2,os_psak,jenis kredit,int_rate'''

    data = string.split("\n")[1:-1]
    data_akhir = []
    for i in data:
        data_akhir.append(i.split(","))
    kolom = kolom.split(",")

    dict_akhir = {}
    for i in kolom:
        dict_akhir[i] = []

    for i in range(len(data_akhir)):
        for j in range(len(data_akhir[i])):
            sementara = dict_akhir[kolom[j]]
            sementara.append(data_akhir[i][j])
            dict_akhir[kolom[j]] = sementara
    df_final = pd.DataFrame(dict_akhir)
    return df_final

def scoring(request,list_data):
    name, dob = list_data.split(";")
    data = read_data() 
    # print(data)
    df_hasil = fuzzy_credit_score(data)
    # print(df_hasil)
    list_sama = df_hasil[name.lower()]
    print(list_sama) 
    # response = {
    #     'cek_user' : cek_user,
    #     'list_data' : list_data
    # }
    return render(request, "main/scoring.html")

def scoring2(request):
#     response = {
#             'cek_user' : cek_user,
#             'list_data' : list_data
#         }
    return render(request, "main/scoring.html")

