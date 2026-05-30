# MzansiPedia

South African stories, history & culture — in a social media feed.

## About

MzansiPedia is a pseudo social media feed that algorithmically shows you content from [Simple Wikipedia](https://simple.wikipedia.org/) — filtered to only South African stories, history, culture, wildlife, and people. The algorithm runs locally on your device and no data leaves your browser.

Once loaded, it works fully offline and can be installed as a PWA.

## Try it

👉 [mzansipedia.org](https://mzansipedia.org) (or [GitHub Pages mirror](https://titidintsako-bit.github.io/mzansipedia/))

## How it works

- A dataset of ~764 South African-themed Wikipedia articles is loaded once.
- Articles are shown as tweet-style cards in an infinite vertical feed.
- The algorithm (simple point-scoring based on categories you engage with) picks what to show next.
- Cards show cached summaries instantly, then fetch fresh text from Wikipedia's live API.
- Click a card to open the full article reader with live Wikipedia content.

## Algorithm

Each post has a set of categories (Wikipedia category tree + pagelinks). Categories earn point scores based on your engagement:

- Scrolling past: -5
- Liking: 50 + 4 × posts since last like
- Clicking to read: 75
- Clicking an image: 100

To pick the next post, 10,000 random articles are sampled and scored. Then:
- 40% chance: weighted random pick (higher score = more likely)
- 42% chance: highest score wins
- 18% chance: completely random

## Dataset

The dataset is generated from [Simple Wikipedia dumps](https://dumps.wikimedia.org/simplewiki/) filtered through South African category patterns and title keywords. See `process_data.py` for the filter logic.

## Fork

This project is a fork of [Xikipedia](https://github.com/rebane2001/xikipedia) by rebane2001. The original concept — Wikipedia as a social media feed — was adapted for South African content and redesigned with a dark theme and expanded features.

## License

AGPLv3. See [LICENSE](LICENSE). The included dataset (`smoldata.json.br`) contains data from Wikipedia, which is available under the [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) license.
