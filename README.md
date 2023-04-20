# Download paper and paper metadata

This is a small app to bulk download arXiv papers. Made so I can start playing around with topic clustering and semantic search, and text models in general. Coded mostly with ChatGPT in an hour or so!

`docker compose up --build`

Take a look in arxiv_scraper.py to change the category and date range to get a smaller subset of papers. The arXiv API docs describe their rate limits and other limitations: https://info.arxiv.org/help/api/tou.html