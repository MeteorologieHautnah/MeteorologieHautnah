#!/usr/bin/env python
"""Read E-mails in the Teilnehmer folder and write them into an Excel file

Call with: `python email_to_excel.py "path/to/your/mbox/file" "path/to/exel/out.xlsx"`

*author*: Johannes Röttenbacher
"""

if __name__ == "__main__":
    import os
    import mailbox
    import sys
    import pandas as pd

    # quick and dirty command line read in
    path = str(sys.argv[1])
    outname = str(sys.argv[2])

    print(f"Input Path: {path}\n")
    print(f"Outname: {outname}\n")

    mbox = mailbox.mbox(path)
    try:
        mbox.lock()
    except mailbox.ExternalClashError:
        # the last lock on the mailbox was probably not removed
        os.remove(f"{path.replace('Teilnehmer', 'Teilnehmer.lock')}")
        mbox.lock()

    df = dict(Nummer=[], Nachname=[], Vorname=[], EMail=[])
    for i, message in enumerate(mbox):
        df["Nummer"].append(i+1)
        parts = message["From"].split(" ")
        if len(parts) == 3:
            df["Vorname"].append(parts[0])
            df["Nachname"].append(parts[1])
            df["EMail"].append(parts[2].replace("<", "").replace(">", ""))
        else:
            # in this case the From does not include a first and last name
            df["EMail"].append(parts[0])
            # try and guess the first and last name
            if parts[0].count(".") == 2:
                # two dots hint at an e-mail address of the form: firstname.lastname@provider.com
                mail_split = parts[0].split(".")
                df["Vorname"].append(mail_split[0].capitalize())
                df["Nachname"].append(mail_split[1].split("@")[0].capitalize())
            else:
                df["Vorname"].append("NA")
                df["Nachname"].append("NA")

    # check that Vorname and Nachname are strings and not yearnumbers
    for i, firstname in enumerate(df["Vorname"]):
        try:
            # try to convert the firstname to an integer, this should throw an error on a normal string
            check = int(firstname)
            # if it succeeds Nachname is a number, replace it with NA
            df["Vorname"][i] = "NA"
        except ValueError:
            pass
        try:
            # try to convert the lastname to an integer, this should throw an error on a normal string
            check = int(df["Nachname"][i])
            # if it succeeds Nachname is a number, replace it with NA
            df["Nachname"][i] = "NA"
        except ValueError:
            pass

    df = pd.DataFrame(df)  # convert dictionary to dataframe
    df.to_excel(outname, index=False)  # save to Excel
    print(f"Saved {outname}")
    mbox.unlock()
