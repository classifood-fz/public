/*
 * Writes test cookie, then deletes test cookie
 */
function browser_accepts_cookies() {
    document.cookie = 'test_cookie=1; path=/';

    if (document.cookie.indexOf('test_cookie') != -1) {
        var expired_date = new Date();
        expired_date.setTime(expired_date.getTime());             
        document.cookie = 'test_cookie=1; path=/; expires=' + expired_date.toGMTString();
        return true;
    }

    return false;
}


/*
 * Finds cookie by name and returns its value
 */
function get_cookie(name) {
    var cookies = document.cookie.split('; ');

    for (var i = 0; i < cookies.length; i++) {
        var pos = cookies[i].indexOf('=');
        if (cookies[i].substr(0, pos) == name) {
            return cookies[i].substr(pos + 1, cookies[i].length - pos + 1);
        }
    }

    return null;
}


/*
 * Adds a cookie or resets existing cookie
 */
function set_cookie(name, value, days, domain, path, secure) {
    if (!name || !value) {
        return false;
    }

    // If params are undefined, set to default values
    days = (typeof days == 'number') ? days : 0;
    domain = (typeof domain == 'string') ? domain : '';
    path = (typeof path == 'string') ? path : '/';
    secure = (typeof secure == 'boolean') ? secure : false;

    var expires = '';

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = date.toUTCString();
    }

    // Build cookie string and then sets cookie
    var cookie = '%s=%s'.replace2('%s', [name, value]);
    cookie += (expires) ? '; expires=' + expires : '';
    cookie += (domain) ? '; domain=' + domain : '';
    cookie += (path) ? '; path=' + path : '';
    cookie += (secure) ? '; secure' : '';
    document.cookie = cookie;
    
    return true;
}


/*
 * Finds cookie by name and sets its expiration time
 * to current time, which expires immediately.
 */
function delete_cookie(name) {
    var cookies = document.cookie.split('; ');

    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].substr(0, cookies[i].indexOf('=')) == name) {
            set_cookie(name, 'delete', -1);
            return true;
        }
    }

    return false;
}
