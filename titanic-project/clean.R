titanic <- read.csv("titanic_original.csv")

# Fill missing embarked with most common port (S = Southampton)
titanic$embarked <- sub("^$", "S", titanic$embarked)

# Impute missing age with column mean
titanic$age[is.na(titanic$age)] <- mean(titanic$age, na.rm = TRUE)

# Normalize boat and cabin fields
titanic$boat <- sub("^$", "None", titanic$boat)
titanic$cabin <- sub("^$", NA, titanic$cabin)

# Binary feature: does passenger have a cabin number?
titanic$has_cabin_number <- ifelse(is.na(titanic$cabin), 0, 1)

write.csv(titanic, file = "titanic_clean.csv", row.names = FALSE)
