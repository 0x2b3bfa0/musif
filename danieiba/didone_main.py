from musif import FeaturesExtractor, FilesValidator

if __name__ == "__main__":

    parts_filter = ["vnI", "vnII", "va", "bs", "sop", "ten", "alt", "bar", "bass", "bbar"]

    arias_dir = "../../Corpus/xml"
    # FilesValidator("config.yml").validate(arias_dir)
    df_scores = FeaturesExtractor("config.yml", parallel=True).extract(arias_dir, parts_filter=parts_filter)
    df_scores.to_csv("myfeatures.csv", index=False)