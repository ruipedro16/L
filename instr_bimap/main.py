#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import csv
import sys
import tqdm


BASE_URL = "https://www.felixcloutier.com/x86/"
OUTPUT_FILE = "asm_instructions.csv"


def write_map_to_csv(map: dict[str, list[str]], filename: str):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Key", "Value"])
        for key, value in map.items():
            writer.writerow([key, value])


def get_asm_instr() -> list[(str, str)]:
    """
    returns (asm instruction, link to the page of that instruction)
    """
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    keys = []
    table = soup.find("table")

    if table:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if cols:
                asm_intr = cols[0].text.strip()
                link = BASE_URL.replace("/x86/", "") + cols[0].find("a")["href"]
                keys.append((asm_intr, link))

    return keys


def get_intrinsics_from_asm_instr(asm_instructions: list[str, str]) -> list[str]:
    lines = []
    for _, instr_url in tqdm.tqdm(asm_instructions, desc="Fetching intrinsics", bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"):

        response = requests.get(instr_url)
        soup = BeautifulSoup(response.content, "html.parser")
        h2_tags = soup.find_all("h2")
        if h2_tags:
            for tag in h2_tags:
                if "Compiler Intrinsic Equivalent" in tag.text:
                    pre_tag = tag.find_next("pre")
                    if pre_tag:
                        lines.append(pre_tag.text)

    return lines


def lines_to_map(lines: list[str]) -> dict[str, list[str]]:
    bimap = {}
    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            key, value = parts
            if key in bimap:
                bimap[key].append(value.strip())
            else:
                bimap[key] = [value.strip()]
    return bimap


def main():
    asm_instructions = get_asm_instr()
    print("Got the list of assembly instructions")
    lines = get_intrinsics_from_asm_instr(asm_instructions)

    filtered_lines = [
        line for line in lines if "Auto-generated from high-level language." not in line
    ]
    
    instr_map = lines_to_map(filtered_lines)
    
    write_map_to_csv(instr_map, OUTPUT_FILE)

    return 0


if __name__ == "__main__":
    sys.exit(main())
