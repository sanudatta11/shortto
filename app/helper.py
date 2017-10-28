from math import floor


def idtoshort_url(id):
    id = int(id)
    map_a = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    shorturl = []
    i = 0
    while(id > 0 and id):
        res = int(id%62)
        shorturl.append(map_a[res])
        id = int(floor(id/62))
        i+=1
    shorturl.reverse()
    ans = ''.join(shorturl)
    return ans

