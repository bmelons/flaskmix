# Flaskmix
or Flaskomix
or Flask Comics
<sub>whatever</sub>

# About
this is a framework made in like a week to host a webcomic in because i don't like using wordpress, it makes me feel dirty and i don't like php either so i made this in python.

this is made for one image per page story comics
i.e no random button 

# Features
- a main series option
- side content option
- admin panel on website.com/admin or website.com/admin


## Environment
make a .env file and add
```
COMIC_ADMIN_COOKIE= value of cookie that is accepted by the admin panel
COMIC_ADMIN_UNAME= admin username
COMIC_ADMIN_PW= admin password
SITE_TITLE= name of site/comic
```

## other instructions

make sure you have three folders in static called
- comic-pages
- side-pages
- chapter-icons

this probably isn't secure but the admin panel is protected by a cookie a single cookie that you can set in the .env file

for most directories it automatically creates them if they don't exist so you don't have to worry about that

updates might fall behind, ill probably fork my comic's site into its own repo
