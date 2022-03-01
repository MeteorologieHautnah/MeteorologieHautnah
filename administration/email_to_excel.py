#!/usr/bin/env python
"""Read E-mails in the Teilnehmer folder and write them into an Excel file

Call with: `python email_to_excel.py "path/to/your/mbox/file" "path/to/exel/out.xlsx"`

*author*: Johannes Röttenbacher
"""


def parse_email(header):
    """
    Given a header from a mbox message like "From" or "Cc" returns the best guess of first name, last name and the
    email address

    :param header: Input from a mbox message

    :return: Tuple with first name, last name and email address
    """
    parts = header.split(" ")
    if len(parts) == 3:
        vorname = parts[0]
        nachname = parts[1]
        email = re.sub(r"[<>]", "", parts[2])
    elif len(parts) == 2:
        # maybe there is only one name given in the From part, ignore it and use only the email address
        # also happens if a Umlaut is involved
        vorname = "NA"
        nachname = "NA"
        email = re.sub(r"[<>]", "", parts[1])
    else:
        # in this case the From does not include a first and last name
        email = re.sub(r"[<>]", "", parts[0])
        # try and guess the first and last name
        if parts[0].count(".") == 2:
            # two dots hint at an e-mail address of the form: firstname.lastname@provider.com
            mail_split = parts[0].split(".")
            vorname = mail_split[0].capitalize()
            nachname = mail_split[1].split("@")[0].capitalize()
        else:
            vorname = "NA"
            nachname = "NA"
    # clean strings and replace numeric characters with NA
    try:
        # try to convert the firstname to an integer, this should throw an error on a normal string
        check = int(vorname)
        # if it succeeds Nachname is a number, replace it with NA
        vorname = "NA"
    except ValueError:
        pass
    finally:
        # remove non-alphanumeric characters
        vorname = re.sub(r'[^a-zA-Z0-9]', '', vorname)
    try:
        # try to convert the lastname to an integer, this should throw an error on a normal string
        check = int(nachname)
        # if it succeeds Nachname is a number, replace it with NA
        nachname = "NA"
    except ValueError:
        pass
    finally:
        # remove non-alphanumeric characters
        nachname = re.sub(r'[^a-zA-Z0-9]', '', nachname)

    return nachname, vorname, email


if __name__ == "__main__":
    import os
    import mailbox
    import sys
    import pandas as pd
    import re

    # quick and dirty command line read in
    path = str(sys.argv[1])
    outname = str(sys.argv[2])

    print(f"Input Path: {path}\n")
    print(f"Outname: {outname}\n")
    emails_to_exclude = ["johannes.roettenbacher@uni-leipzig.de", "ritter@tropos.de", "jakob.thoboell@web.de"]

    mbox = mailbox.mbox(path)
    try:
        mbox.lock()
    except mailbox.ExternalClashError:
        # the last lock on the mailbox was probably not removed
        os.remove(f"{path.replace('Teilnehmer', 'Teilnehmer.lock')}")
        mbox.lock()

    df = pd.DataFrame(dict(Nachname=[], Vorname=[], EMail=[]))
    for message in mbox:
        df.loc[len(df.index)] = parse_email(message["From"])

        # check the CC and add that also to the participant list
        try:
            parts = message["Cc"].split(" ")
            nachname, vorname, email = parse_email(message["Cc"])
            if any(mail in email for mail in emails_to_exclude):
                pass
            else:
                df.loc[len(df.index)] = [nachname, vorname, email]
        except AttributeError:
            # in this case a None Object is returned which does not have a split method -> no Cc
            pass

    df.to_excel(outname, index_label="Nummer")  # save to Excel
    print(f"Saved {outname}")
    mbox.unlock()
