from django.shortcuts import render
from fuzzywuzzy import fuzz
import numpy as np
import pandas as pd

def home(request):
    return render(request, "main/home_start.html")


def home2(request):
    return render(request, "main/home2.html")

def scoring(request):
    return render(request, "main/scoring.html")

def score_fuzzy(df):
    nama = np.char.lower(list(df["nama"]))
    ibu_kandung = np.char.lower(list(df["ibu_kandung"]))
    # alamat = np.char.lower(list(df["alamat"]))
    hasil = np.array([])
    for i in range(len(nama)):
        for j in range(len(nama)):
            score = 0
            if i != j:
                score_nama = fuzz.ratio(nama[i], nama[j])
                score_nama_2 = fuzz.token_sort_ratio(nama[i], nama[j]) # split perkata sebelum diperiksa ratio menggunakan levenshtein
                if score_nama_2> score_nama:
                    score_nama = score_nama_2
                score_ibu = fuzz.ratio(ibu_kandung[i], ibu_kandung[j])
                score_ibu_2 = fuzz.token_sort_ratio(ibu_kandung[i], ibu_kandung[j]) # split perkata sebelum diperiksa ratio menggunakan levenshtein
                if score_ibu_2> score_ibu:
                    score_ibu = score_ibu_2
                # score_alamat = fuzz.ratio(alamat[i],alamat[j])
                # score_alamat_2 = fuzz.token_sort_ratio(alamat[i],alamat[j]) # split perkata sebelum diperiksa ratio menggunakan levenshtein
                # if score_alamat_2>score_alamat:
                #     score_alamat = score_alamat_2
                # score = score_nama + score_ibu + score_alamat
                score = score_nama + score_ibu
                if score_nama <= 20: # batas bawah seseorang dianggap memiliki nama yang sama
                    score = 0
                if score_ibu <= 20: # batas bawah seseorang dianggap memiliki nama ibu yang sama
                    score = 0
                hasil = np.append(
                    hasil,
                    nama[i]+" dan "+nama[j]+" : "+
                    "\n score nama : "+str(score_nama)+" ("+nama[i]+" & "+nama[j]+")"+
                    "\n score ibu : "+str(score_ibu)+" ("+ibu_kandung[i]+" & "+ibu_kandung[j]+")"+
                    # "\n score alamat : "+str(score_alamat)+" ("+alamat[i]+" & "+alamat[j]+")"+
                    "\n score total : "+str(score)
                    )
    return hasil