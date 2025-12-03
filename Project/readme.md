# IMDb & Wikimedia Streaming Project

## 1. General overview

This project has two objectives:

1. Perform a **data analysis** on the IMDb datasets  
   (`name.basics.tsv`, `title.basics.tsv`, `title.ratings.tsv`, `title.crew.tsv`, etc.).
2. Set up a **stream processing** pipeline on Wikimedia events  
   in order to track pages related to certain entities (movies, people, genres).

The work is carried out by a group of 5 students:

- Berkani Mohammed Adam  
- Bellouch Ayoub  
- Mafkoud Khaoula  
- Hamid Hiba  
- Brunel Nangoum-Tchatchoua  

The main code is contained in the notebook:

- `analyse_imdb.ipynb`

The streaming part is implemented in:

- `wikimedia_stream.py`


## 2. IMDb data

The IMDb files were taken from the Teacher's datasets, they contain:

Main files:

- `name.basics.tsv`
- `title.basics.tsv`
- `title.ratings.tsv`
- `title.crew.tsv`
- `title.akas.tsv` (loaded in chunks due to its size)

---

## 3. Structure of the `analyse_imdb.ipynb` notebook

The notebook is organized by **questions**:

### Q1 – Total number of people

- Read `name.basics.tsv`
- Use `len(names)` to count the total number of people.

### Q2–Q3 – Earliest year of birth and corresponding age

- Convert `birthYear` to numeric.
- Observe an anomalous minimum year (`4`), highlighted in the notebook.
- Define a realistic lower bound (`birthYear >= 1800`).
- Compute:
  - the earliest realistic year of birth,
  - the corresponding age in the current year.

### Q4 – Validation of the birth year “4”

- Retrieve people with `birthYear = 4`.
- Use the `knownForTitles` column to retrieve the corresponding works  
  from `title.basics`.
- Compare the year of birth with the year of the first listed work:  
  the resulting age (more than 1900 years) shows that the birth year is **not realistic**.
- Conclusion: `birthYear = 4` is an **outlier / erroneous value**.

### Q5 – Most recent year of birth

- Find the maximum value of `birthYear` while excluding future years.

### Q6 – Percentage of people without a birth year

- Count `NaN` values in `birthYear`.
- Compute the percentage of people **without a recorded year of birth**.

### Q7 – Length of the longest “short” after 1900

- Filter `title.basics`:
  - `titleType = "short"`
  - `startYear > 1900`
  - `runtimeMinutes > 0`
- Find the maximum duration.
- Display the title, year, and duration (in minutes).

### Q8 – Duration of the shortest “movie” after 1900

- Filter `title.basics`:
  - `titleType = "movie"`
  - `startYear > 1900`
  - `runtimeMinutes > 0`
- Find the minimum duration.
- Display the title, year, and duration (in minutes).

### Q9 – List of all genres represented

- Use the `genres` column (a string such as `"Action,Comedy"`).
- Split by `,`, explode, then extract unique values.
- Sort them alphabetically and display the full list.

### Q10 – Best comedy movie, director(s), and alternative titles

1. **Best comedy movie**
   - Filter titles of type `movie` whose `genres` contain `"Comedy"`.
   - Join with `title.ratings`.
   - Select the movie with the highest `averageRating`.
   - In case of a tie, select the one with the highest `numVotes`.

2. **Director(s)**
   - Retrieve the movie’s `tconst`.
   - Look it up in `title.crew` (field `directors`).
   - Join with `name.basics` to obtain the directors’ names.

3. **Alternative titles**
   - Read `title.akas.tsv` in chunks (`chunksize`).
   - Filter on `titleId = tconst of the best comedy movie`.
   - Display the columns `title`, `region`, `language`, `isOriginalTitle`.

All numeric answers are summarized again in **Markdown** cells in the notebook.

---

## 4. Wikimedia stream processing

The streaming part is implemented in the script:

- `wikimedia_stream.py`

### 4.1 Tracked entities

We track 5 entities that have an English Wikipedia page:

- Bob vs. Society  
- Lucio Anneo Seneca  
- Our First Day  
- Comedy film  
- Drama film  

These entities are defined in the `ENTITIES` list in the script.

### 4.2 Script logic

1. Connect to the Wikimedia streaming API:

   - URL: `https://stream.wikimedia.org/v2/stream/recentchange`
   - Filter on the `enwiki` wiki.

2. For each received event:

   - Check whether the page title matches one of the tracked entities.
   - If it does, extract:
     - `timestamp`
     - `wiki`
     - `title`
     - `user`
     - `type`
     - `comment`
     - `old_len`
     - `length` (page size after the edit)
     - `size_diff` (difference in size)

3. Events are stored in:

   - `data/wiki_events.csv`

   with the columns:

   - `timestamp`, `wiki`, `title`, `entity_match`, `user`, `type`,  
     `comment`, `old_len`, `new_len`, `size_diff`.

### 4.3 Alert system

The script simulates an alert system by detecting two types of situations:

- edits made by a specific user (`TARGET_USER`),
- large edits (`|size_diff| >= SIZE_THRESHOLD`).

Alerts are stored in:

- `data/wiki_alerts.csv`

with the columns:

- `timestamp`, `wiki`, `title`, `entity_match`, `user`, `type`,  
  `comment`, `reason`, `old_len`, `new_len`, `size_diff`.

A `[ALERT]` message is also printed in the console.

### 4.4 Execution

From the project root:

- pip install -r requirements.txt   # if you have defined a dependency file
- python wikimedia_stream.py

### 5. Individual contributions

- Each group member contributed to specific parts of the project:

### Berkani Mohammed Adam

- Set up the project structure and data folder.

- Implemented the loading and cleaning of IMDb datasets (names, titles, ratings, crew).

- Wrote and tested the solutions for Q1–Q4 (earliest birth year and consistency check).

### Bellouch Ayoub

- Implemented the analyses for Q5–Q7 (most recent birth year, missing birth years, longest short).

- Helped with numeric conversions (startYear_num, runtime_num) and data quality checks.

- Contributed to the organization and commenting of the notebook code.

### Mafkoud Khaoula

- Implemented the logic for Q8–Q10 (shortest movie, best comedy movie, directors, alternative titles).

- Worked on joining IMDb tables (titles, ratings, crew, names, akas).

- Helped to handle large files using chunked reading (chunksize).

### Hamid Hiba

- Developed and tested the wikimedia_stream.py streaming script.

- Designed the event and alert formats (wiki_events.csv, wiki_alerts.csv).

- Ensured that all notebooks and scripts run successfully from start to finish.

### Brunel Nangoum-Tchatchoua

- Added placeholder filenames and notes for potential future streaming features.

- Performed a light review of the repository structure and formatting.
  
- Wrote and structured the Markdown explanations for Q1–Q10.




