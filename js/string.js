/*
 * replace2 replaces every str in a string if
 * there are arr.length or less strs in the string
 */
String.prototype.replace2 = function (str, arr) {
    var result = this.toString();

    for (var i = 0; i < arr.length; i++) {
        result = result.replace(str, arr[i]);
    }

    return result;
}

/*
 * upfirst capitalizes the first letter of
 * every word in the string
 */
String.prototype.upFirst = function () {
    var words = this.split(' ');

    for (var i=0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1, words[i].length - 1);
    }

    return words.join(' ');
}

/*
 * escapeSingleQuotes replaces every occurrance of
 * ' with \'
 */
String.prototype.escapeSingleQuotes = function() {
        var s = this.toString();
        var s2 = '';

	for (var i=0; i<s.length; i++) {
	    if (s[i] == "'") {
		s2 += "\\'";
	    }
            else {
		s2 += s[i];
	    }
        }

	return s2;
}
