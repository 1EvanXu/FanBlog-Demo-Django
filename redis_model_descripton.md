|No.|Data type|Key Name|details|
| --------|--------|--------|--------|
|1|hash|pub_article:[pub_id]|keys->[title, type, category, absract, pub_time, link, votes_count, visitors_count, comments_count]|
|2|zset|articles_rank:|
|3|list|all_pub_articles:|
|4|zset|voted:[pub_id]|
|5|zset|article_visitors_record:[pub_id]|
|6|zset|visitors_records:|
|7|zset|region_distributions:|
|8|string|article_content:[md-html]:[article_id]|
|9|zset|PV_counters:|
|10|zset|PV_counter:[300-7200-86400]



|api|
|--------|
|get_redis_connection()|
|publish_record(pub_id, title, pub_type, category, link, abstract='', conn=__CONNECTION)|
|delete_publish_record(pub_id, conn=__CONNECTION)|
|article_vote_record(voter, pub_id, conn=__CONNECTION|
|has_voted(visit_record, pub_id, conn=__CONNECTION)|
|article_visit_record(visitor, pub_id, conn=__CONNECTION)|
|blog_visit_record(visit_record, conn=__CONNECTION)|
|load_content(article_id, file_path, file_type='md', conn=__CONNECTION)|
|save_content(article_id, content_value, file_type="md", conn=__CONNECTION)|
|update_comments_count(pub_id, conn=__CONNECTION)|
|hgetall_pub_article(pub_article, conn=__CONNECTION)|
|update_PV_counter(count=1, conn=__CONNECTION)|
|get_PV_counter(precision, conn=__CONNECTION)|
