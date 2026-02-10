# Config
## Preferences 
- **enableRandomButton** *bool*: 
    - Does the comic(s) template contain a button to send the reader to a random page of the comic? 
- **enableCharactersPage** *bool*: 
    - Does the site have a page which displays a list of images, as a character showcase?
- **enableSidecomics** *bool*: 
    - Does the site host comics other than the main one?
- **enablePageList** *bool*: 
    - Does the site have a page that displays a list of page links with their descriptions?
- **enableChapterList** *bool*: 
    - Does the site have a page that displays a list of chapters/sections of the comic?
- **enableTags** *bool*: 
    - Does the site have tags for the pages, and a page browse by year/month/tag
## Auto-Tags
- **date** : *int/enum*
    - **0**: No date tagging
    - **1**: Date tagging by year
    - **2**: Date tagging by month of year 

## Theming
- **chaptersName** : *str*
    - How the site refers to chapters (e.g. chapters, volumes, arcs, sections)
- **pagesName** : *str*
    - How the site refers to pages (e.g. pages, panels, strips)
- **~~baseColor~~** : *array[3]*
    - stub/unimplemented, some css and js stuff has to be done before this is
    - rgb color that the site is themed around


# Default
```
{
  "preferences": {
    "enableCharactersPage": true,
    "enableSideComics": true,
    "enablePageList": true,
    "enableChapterList": true,
    "enableTags": true,
    "enableRandomButton": true,
  },
  "autoTags": {
    "date": 2
  },
  "theming": {
    "chaptersName": "Chapters",
    "pagesName": "Pages",
    "baseColor": [255, 255, 255]
  }
}
```