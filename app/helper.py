def idtoshort_url(id):
    map_a = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    shorturl = []
    while(id):
        shorturl.append(map_a[id%62])
        id = id/62
    shorturl.reverse()
    ans = ''.join(shorturl)
    return ans
