# india-mplads-works

Dataset of spending on MPLADS developmental works by Indian parliamentary representatives. Sourced from [the MPLADS site](http://164.100.68.116/mpladssbi/Default.aspx).

Browse the dataset here: <https://flatgithub.com/Vonter/india-mplads-works?filename=csv/MPLADS.csv&stickyColumnName=MP%20NAME&sort=RECOMMENDED%20DATE%2Cdesc>.

**Note: The MPLADS site contains MPLADS reports from 1st April 2023 onwards.**

## Scripts

- [fetch.py](fetch.py): Fetches the raw HTML pages from [the MPLADS site](http://164.100.68.116/mpladssbi/Default.aspx)
- [flatten.py](flatten.py): Parses the raw HTML pages, and generates the CSV dataset

## License

This india-mplads-works dataset is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. 
Users of this data should attribute [the MPLADS site](http://164.100.68.116/mpladssbi/Default.aspx)

You are free:

* **To share**: To copy, distribute and use the database.
* **To create**: To produce works from the database.
* **To adapt**: To modify, transform and build upon the database.

As long as you:

* **Attribute**: You must attribute any public use of the database, or works produced from the database, in the manner specified in the ODbL. For any use or redistribution of the database, or works produced from it, you must make clear to others the license of the database and keep intact any notices on the original database.
* **Share-Alike**: If you publicly use any adapted version of this database, or works produced from an adapted database, you must also offer that adapted database under the ODbL.
* **Keep open**: If you redistribute the database, or an adapted version of it, then you may use technological measures that restrict the work (such as DRM) as long as you also redistribute a version without such measures.

## Generating

Ensure you have `python` installed with the required dependencies (`selenium`, `beautifulsoup4`)

```
# Fetch the data
python fetch.py

# Generate the CSV
python flatten.py
```

The fetch script sources data from the MPLADS site (http://164.100.68.116/mpladssbi/Default.aspx)

## TODO

- Extend dataset with additional columns
  - `pc_id` for mapping to [Parliamentary Constituencies Shapefile (2019)](https://github.com/datameet/maps/blob/master/parliamentary-constituencies/india_pc_2019_simplified.geojson)
  - `code` for mapping to [LGD Codes](https://ramseraph.github.io/opendata/lgd/)

## Credits

- [MPLADS site](http://164.100.68.116/mpladssbi/Default.aspx)

## Related

- [india-election-affidavits](https://github.com/Vonter/india-election-affidavits)
- [india-representatives-activity](https://github.com/Vonter/india-representatives-activity)
