mkdir 'log'&>/dev/null
mkdir '../wordtree'&>/dev/null

rm 'ingredients.txt'&>/dev/null
scrapy runspider 'scraper/spiders/edible_seeds.py' &> 'log/edible_seeds.log'
mv 'ingredients.txt' '../wordtree/'
