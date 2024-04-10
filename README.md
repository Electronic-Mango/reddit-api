# Reddit API API

[![CodeQL](https://github.com/Electronic-Mango/reddit-api-api/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Electronic-Mango/reddit-api-api/actions/workflows/codeql-analysis.yml)
[![Black](https://github.com/Electronic-Mango/reddit-api-api/actions/workflows/black.yml/badge.svg)](https://github.com/Electronic-Mango/reddit-api-api/actions/workflows/black.yml)
[![Flake8](https://github.com/Electronic-Mango/reddit-api-api/actions/workflows/flake8.yml/badge.svg)](https://github.com/Electronic-Mango/reddit-api-api/actions/workflows/flake8.yml)


> [!NOTE]
> I've created a new version of this API using FastAPI, you can find it here: https://github.com/Electronic-Mango/reddit-fastapi-api.
> 
> I recommend using it over this version, as this one is no longer maintained.
> FastAPI version has the same functionality (or even more as it includes Swagger/ReDoc documentation!) while being a lot simpler than this one.


A simple Reddit REST API allowing accessing both subreddit and user articles,
build with [`Flask`](https://github.com/pallets/flask/) and my [`Reddit Python API`](https://github.com/Electronic-Mango/reddit-python-api)!



## Table of contents

 - [Introduction and requirements](#introduction-and-requirements)
 - [Configuration](#configuration)
   - [API parameters](#api-parameters)
   - [Reddit app & required parameters](#reddit-app--required-parameters)
   - [Docker](#docker)
 - [Additional authorization](#additional-authorization)
 - [Running the API](#running-the-api)
   - [From source](#from-source)
   - [Docker](#docker-1)
 - [API endpoints](#api-endpoints)
   - [Get a list of articles from a subreddit](#get-a-list-of-articles-from-a-subreddit)
   - [Get one random article from a subreddit](#get-one-random-article-from-a-subreddit)
   - [Get a list of articles from a Reddit user](#get-a-list-of-articles-from-a-reddit-user)
   - [Get a random article from a Reddit user](#get-a-random-article-from-a-reddit-user)
 - [Filtering and article types](#filtering-and-article-types)
   - [Reddit galleries](#reddit-galleries)
 - [Load count](#load-count)
 - [Disclaimer](#disclaimer)



## Introduction and requirements

This REST API was built using [`Flask`](https://github.com/pallets/flask/), my [`Reddit Python API`](https://github.com/Electronic-Mango/reddit-python-api)  and `Python 3.11`.
Python version at least `3.11` is required.

Full list of Python requirements is in `requirements.txt` file.

Technically this API only *wraps* parts of official Reddit API, thus *Reddit API **API***.
However, accessing Reddit API itself through external services is quite cumbersome, due to necessary OAuth 2.0 authorization.
This API allows external services to access API through simple HTTP requests, without worrying about access tokens, Reddit app client, etc.
It also allows for simple access to specific services, like reading only one random article or reading only media or text articles, without any additional processing.

This API uses my simple [`Reddit Python API`](https://github.com/Electronic-Mango/reddit-python-api) to access official Reddit API.

No data is stored by the API.
Reddit is accessed in `read-only` mode.
API requests can optionally be authenticated based on request header.

You can check my other repository [Memes Discord bot Docker deployment](https://github.com/Electronic-Mango/memes-discord-bot-docker-deployment) for an example of how you can use this API in a Discord bot, deployed via Docker Compose.



## Configuration

### API parameters

API configuration can be done through a YAML configuration file.
By default `settings.yml` from the project root is used, which has some sensible defaults, other than [Reddit API client ID and secret](#reddit-app--required-parameters).

You can overwrite values from default `settings.yml` by providing a custom one under path from `CUSTOM_SETTINGS_PATH` environment variable.
In this custom YAML you can provide only parameters which you want to overwrite.
If parameter is absent in the custom one, then default value from `settings.yml` will be used.

Value for `CUSTOM_SETTINGS_PATH` can also be provided via `.env` file in the project root.


### Reddit app & required parameters

To run the API you need to first register a Reddit app at https://old.reddit.com/prefs/apps/.
There are two fields which need to be filled in `reddit` - `client` section in `settings.yml` based on your app - `id` and `secret`.
Those values will be used to acquire OAuth 2.0 token from Reddit API itself. 

No other data is necessary, since the API works in `read-only` mode.


### Docker

There's a `Dockerfile` in the repo, which will build a Docker image for the API using `python:3.12-alpine` as base.
You can set all configuration parameters using environment variables for Docker container, rather than modifying project files before building.

You can also use `docker-compose.yml` to build and start the container via:

```
docker compose up -d --build
```

Compose allows using `custom_settings.yml` in project root for custom configuration, like [Reddit app ID and secret](#reddit-app--required-parameters) without modifying project files.
By default, this file will be loaded into the image, along with all `.yml` files from the project root.

You can get around this by modifying value of `CUSTOM_SETTINGS_PATH` in `docker-compose.yml` to point to a file in a mounted volume.

Default port where API requests are handled is `8080`, which is mapped to local port `3001`.



## Additional authorization

Api has a basic authorization mechanism based on request header, separate from Reddit API OAuth 2.0.
You can set authorization header name and expected value in `settings.yml` in `api` - `authorization_header` - `name` and `expected_value`.

If either of them is empty authorization will be disabled and all requests will be accepted.

If both fields are filled, then any request which doesn't have a header named `name` with value `expected_value` will be rejected with code `401`.

By default, without any changes to `settings.yml` authorization is disabled.



## Running the API

First you need to register a Reddit app and note its ID and secret.


###  From source

 1. Install all packages from `requirements.txt`
 2. Fill Reddit app ID and secret either in `settings.yml` or in a custom one
 3. Run `src/main.py` via Python


### Docker

 1. Fill Reddit app ID and secret in `settings.yml` or in `custom_settings.yml`
 2. Run `docker compose up -d --build`

You can skip `--build` flag on subsequent runs if you didn't change the source code, but keep in mind that by default `custom_settings.yml` is added to the docker image.
Any changes there will require image rebuild.

You can get around this by modifying value of `CUSTOM_SETTINGS_PATH` in `docker-compose.yml` to point to a file in a mounted volume.



## API endpoints

All endpoints are accessible via `GET` requests.
If request authorization is configured incoming requests needs to have correct header and its value.

### Get a list of articles from a subreddit

Endpoint:
```
/subreddit/{article_type}/{subreddit_name}/{load_count}/{sort_type}
```

| Parameter          | Description                                                            | Optional | Default value |
|--------------------|------------------------------------------------------------------------|----------|---------------|
| `{article_type}`   | Whether to load all articles, only text or only images                 | No       |               |
| `{subreddit_name}` | Name of subreddit to load articles from, including `all` and `popular` | Yes      | `all`         |
| `{load_count}`     | How many articles to load                                              | Yes      | `50`          |
| `{sort_type}`      | Which Reddit sorting type to use when loading articles                 | Yes      | `hot`         |

`{article_type}` can be one of the following:

 - `article` - all articles
 - `media` - only media articles
 - `text` - only articles where `selftext` is not empty

`{sort_type}` can be one of the following:

 - `top`
 - `new`
 - `controversial`
 - `hot`

`{load_count}` and `{sort_type}` can be omitted, but both have to be specified when you want to specify `{sort_type}`.


Example request:
```
GET /subreddit/article/wholesomememes/3/top
```

Example response:
```json
{
  "count": 3,
  "articles": [
    {
      "author": "Boreol",
      "created_utc": "Mon, 15 Aug 2022 11:22:19 GMT",
      "id": "wov1zd",
      "media_url": "https://i.redd.it/4xmwndm1iuh91.png",
      "nsfw": false,
      "permalink": "/r/wholesomememes/comments/wov1zd/hes_gonna_be_getting_all_the_ladies/",
      "score": 55263,
      "selftext": "",
      "spoiler": false,
      "stickied": false,
      "subreddit": "wholesomememes",
      "title": "He's gonna be getting all the ladies",
      "url": "https://i.redd.it/4xmwndm1iuh91.png"
    },
    {
      "author": "deserr",
      "created_utc": "Sun, 14 Aug 2022 22:57:27 GMT",
      "id": "wogjes",
      "media_url": "https://i.redd.it/ayi2nev5tqh91.jpg",
      "nsfw": false,
      "permalink": "/r/wholesomememes/comments/wogjes/looking_for_my_sweet_potato/",
      "score": 27241,
      "selftext": "",
      "spoiler": false,
      "stickied": false,
      "subreddit": "wholesomememes",
      "title": "Looking for my sweet potato 🥺",
      "url": "https://i.redd.it/ayi2nev5tqh91.jpg"
    },
    {
      "author": "hackyandbird",
      "created_utc": "Sun, 14 Aug 2022 23:40:27 GMT",
      "id": "wohizo",
      "media_url": "https://i.redd.it/vjbg1xcs0rh91.gif",
      "nsfw": false,
      "permalink": "/r/wholesomememes/comments/wohizo/sign_me_up/",
      "score": 22436,
      "selftext": "",
      "spoiler": false,
      "stickied": false,
      "subreddit": "wholesomememes",
      "title": "Sign me up",
      "url": "https://i.redd.it/vjbg1xcs0rh91.gif"
    }
  ]
}
```

For images and GIFs `media_url` field is the same as `url`.
For videos, it will be a different URL.


### Get one random article from a subreddit

Endpoint:
```
/subreddit/{article_type}/random/{subreddit_name}/{load_count}/{sort_type}
```

All parameters are the same as for [loading a list of articles for a subreddit](#get-a-list-of-articles-from-a-subreddit).

`{load_count}` determines how many articles will be loaded, a random one will be selected from them.


Example request:
```
GET /subreddit/text/random/explainlikeimfive/100/top
```

Example response:
```json
{
  "author": "streetpony445",
  "created_utc": "Mon, 15 Aug 2022 00:59:12 GMT",
  "id": "wojb18",
  "media_url": null,
  "nsfw": false,
  "permalink": "/r/explainlikeimfive/comments/wojb18/eli5_what_is_negative_pressure/",
  "score": 1,
  "selftext": "I was listening to an astronomy talk at an observatory and the speaker mentioned “negative pressure”. How is that even possible",
  "spoiler": false,
  "stickied": false,
  "subreddit": "explainlikeimfive",
  "title": "eli5: what is negative pressure?",
  "url": "https://www.reddit.com/r/explainlikeimfive/comments/wojb18/eli5_what_is_negative_pressure/"
}
```


### Get a list of articles from a Reddit user

Endpoint:
```
/user/{article_type}/{user_name}/{load_count}/{sort_type}
```

All parameters are the same as for [loading a list of articles for a subreddit](#get-a-list-of-articles-from-a-subreddit), except for providing a Reddit username instead of subreddit name.
Username parameter is required, unlike subreddit.

Example request:
```
GET /user/media/cme_t/3
```

Example response:
```json
{
  "count": 2,
  "articles": [
    {
      "author": "CME_T",
      "created_utc": "Mon, 25 Jul 2022 18:08:12 GMT",
      "id": "w7stzz",
      "media_url": "https://i.redd.it/fzworhhimqd91.jpg",
      "nsfw": false,
      "permalink": "/r/TheWeeklyRoll/comments/w7stzz/ch_124_common_knowledge/",
      "score": 5366,
      "selftext": "",
      "spoiler": false,
      "stickied": false,
      "subreddit": "TheWeeklyRoll",
      "title": "Ch. 124. \"Common knowledge\"",
      "url": "https://i.redd.it/fzworhhimqd91.jpg"
    },
    {
      "author": "CME_T",
      "created_utc": "Mon, 25 Jul 2022 18:08:00 GMT",
      "id": "w7stti",
      "media_url": "https://i.redd.it/4kid37rjmqd91.jpg",
      "nsfw": false,
      "permalink": "/r/DnD/comments/w7stti/artoc_the_weekly_roll_ch_124_common_knowledge/",
      "score": 1913,
      "selftext": "",
      "spoiler": false,
      "stickied": false,
      "subreddit": "DnD",
      "title": "[Art][OC] The Weekly Roll Ch. 124. \"Common knowledge\"",
      "url": "https://i.redd.it/4kid37rjmqd91.jpg"
    }
  ]
}
```

Notice that 3 media articles were requested, but response only contains 2.
It's because out of 3 loaded articles only 2 were images.

Also, since `{sort_type}` was omitted default value of `hot` was used.


### Get a random article from a Reddit user

Endpoint:
```
/user/{article_type}/random/{user_name}/{load_count}/{sort_type}
```

All parameters are the same as for [loading a list of articles for a Reddit user](#get-a-list-of-articles-from-a-reddit-user).

Example request:
```
GET /user/media/random/cme_t/
```

Example response:
```json
{
  "author": "CME_T",
  "created_utc": "Sun, 17 Jul 2022 21:41:08 GMT",
  "id": "w1fkap",
  "media_url": "https://i.redd.it/2oikh0bvl6c91.jpg",
  "nsfw": false,
  "permalink": "/r/TheWeeklyRoll/comments/w1fkap/ch_123_were_shorthanded_af/",
  "score": 5600,
  "selftext": "",
  "spoiler": false,
  "stickied": false,
  "subreddit": "TheWeeklyRoll",
  "title": "Ch. 123. \"We're short-handed af\"",
  "url": "https://i.redd.it/2oikh0bvl6c91.jpg"
}
```

Since both `{load_count}` and `{sort_type}` were omitted, the default values of `50` and `hot` were used.


## Filtering and article types

Other than all articles, API allows for filtering article types.
The two filters are `text` and `media`.

For `text` all articles where `selftext` is not empty are selected.

For `media` there are two cases, one for images and one for videos:

 - images are detected based on `i.redd.it` domain **OR** `post_hint` equal to `image`, since not all subreddits have `post_hint`
 - videos are detected based on `v.redd.it` domain **AND** `is_video` equal to `True`, there are some posts where domain is `v.redd.it`, but there are no necessary URLs

In case of videos, resulting `media_url` URL has `?source=fallback` trimmed out, so it ends with file extension.


### Reddit galleries

Currently, galleries won't be filtered into `media` category and their media URLs aren't easily accessible.



## Load count

When specifying how many articles should be loaded the final count can be lower.

For all articles this can occur if a given subreddit or user has fewer articles than specified.

For text and media articles the passed value only determines how many articles are loaded from Reddit overall.
This value can be later lowered as only specific type of articles are filtered from the list of all articles.
Not additional articles are loaded after filtering.

Load count also impacts retrieving one random article.
This one random article is picked from a loaded selection, instead of sending all of them.
Actual count of articles to pick from can be lowered due to additional filtering, as before.

Still, the higher the load count the lower the odds of selecting the same random article on subsequent API calls.



## Disclaimer

This bot is in no way affiliated, associated, authorized, endorsed by, or in any way officially connected with Reddit.
This is an independent and unofficial project.
Use at your own risk.
