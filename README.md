# MzansiPedia

South African Wikipedia stories in a local-first reading feed.

## About

MzansiPedia turns South African Wikipedia topics into a reading feed. It is filtered toward South African history, culture, places, people, sport, wildlife, languages, and food.

Your likes, profile, and ranking scores stay in browser storage. The bundled dataset works offline after it loads; live article summaries and images are requested from Wikipedia and Wikimedia when a network is available.

## Try it

- [Vercel](https://mzansipedia.vercel.app/)
- [GitHub Pages mirror](https://titidintsako-bit.github.io/mzansipedia/)

## Open source and privacy

The repository is public on GitHub under AGPLv3. The app does not require accounts, API keys, server-side databases, or analytics.

Profile choices, likes, ranking scores, and collections stay in local browser storage. Network requests go to the hosted static files and to Wikipedia/Wikimedia article summary and image endpoints while browsing.

Do not commit local `.env*`, `.vercel/`, dependency folders, or generated test output; those paths are ignored.

## How it works

- A dataset of ~764 South African-themed Wikipedia articles is loaded once.
- Articles are shown as tweet-style cards in an infinite vertical feed.
- The algorithm (simple point-scoring based on categories you engage with) picks what to show next.
- Cards show bundled summaries instantly, then fetch fresh text from Wikipedia's live API when online.
- Click a card to open the full article reader with live Wikipedia content.
- Filter the feed by topic lenses such as History, People, Places, Culture, Wildlife, and Sport.
- Save articles into local collections and generate shareable knowledge cards.
- Article pages suggest related follow-up reads from the local dataset.

## Algorithm

Each post has a set of categories (Wikipedia category tree + pagelinks). Categories earn point scores based on your engagement:

- Scrolling past: -5
- Liking: 50 + 4 x posts since last like
- Clicking to read: 75
- Clicking an image: 100

To pick the next post, 10,000 random articles are sampled and scored. Then:
- 40% chance: weighted random pick (higher score = more likely)
- 42% chance: highest score wins
- 18% chance: completely random

## Dataset

The dataset is generated from [Simple Wikipedia dumps](https://dumps.wikimedia.org/simplewiki/) filtered through South African category patterns and title keywords. See `process_data.py` for the filter logic.

## Fork

This project is a fork of [Xikipedia](https://github.com/rebane2001/xikipedia) by rebane2001. The original concept - Wikipedia as a social media feed - was adapted for South African content and redesigned with a dark theme and expanded features.

## License

AGPLv3. See [LICENSE](LICENSE). The included dataset (`smoldata.json.br`) contains data from Wikipedia, which is available under the [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) license.
