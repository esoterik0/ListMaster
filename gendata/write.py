from npcdat import names_female_short, names_male_short

if __name__ == "__main__":
    with open('ffirst.txt', 'w') as f:
        for name in names_female_short:
            f.write(name)
            f.write('\n')

    with open('mfirst.txt', 'w') as f:
        for name in names_male_short:
            f.write(name)
            f.write('\n')
