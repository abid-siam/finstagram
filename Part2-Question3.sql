SELECT photoID FROM share
NATURAL JOIN belong
NATURAL JOIN closefriendgroup
WHERE belong.username = "Ann";