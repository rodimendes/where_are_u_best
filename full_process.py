from main_tasks import matches


# URL TO GET SOURCE CODE
urls = input("Paste the url [or urls separated by comma] from WTA to iniciate the process: ").split(',')

for url in urls:
    # GETTING THE SOURCE CODE AND SAVING IT FOR FURTHER VERIFICATIONS
    print("Getting the source code and saving it for further verifications")
    source_code = matches.get_source_code(url=url.strip())
    print(f"Getting \033[92m\033[1m{source_code[1]}\033[0m raw data")

    # EXTRACTING DATA FROM SOURCE CODE AND BUILDING A DICTIONARY
    print("Extracting data from source code and building a dictionary")
    data_dict = matches.get_matches_info_to_dict(source_code=source_code[0])

    # TRANSFORMING DICTIONARY INTO DATAFRAME, CHECKING DUPLICATE DATA AND SAVING CLEANED DATA AS PICKLE FILE
    print("Transforming dictionary into dataframe, cheking duplicate data and saving cleaned data as pickle file")
    data_df = matches.to_dataframe(player_name=source_code[1], player_matches=data_dict)

    # SAVING DATA INTO DATABASE
    print("Saving data into database")
    matches.to_database(dataframe=data_df)

# urls = https://www.wtatennis.com/players/318176/beatriz-haddad-maia#matches, https://www.wtatennis.com/players/326408/iga-swiatek#matches, https://www.wtatennis.com/players/320760/aryna-sabalenka#matches, https://www.wtatennis.com/players/326735/leylah-fernandez#matches
