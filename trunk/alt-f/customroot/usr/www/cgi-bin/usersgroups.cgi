#!/bin/sh

. common.sh
check_cookie
write_header "Users and Groups Setup"

CONFP=/etc/passwd
CONFG=/etc/group

BRD=0

if ! test -h /home -a -d "$(readlink -f /home)"; then
	cat<<-EOF
		<h4>No users directory found, create it in:</h4>
		<form action="/cgi-bin/newuser_proc.cgi" method=post>
	EOF
	# FIXME offer possibility of creation of Public directories
	select_part
	echo "</select><input type=submit name=create_dir value=CreateDir>
		</form></body></html>"
	exit 0
fi

cat <<EOF
	<script type="text/javascript">
	var users = new Array();
	var groups = new Array();
	var groupsInUser = new Array();
	var usersInGroup = new Array();
	function update_users() {
		document.frm.uname.value = document.frm.users.value;
		document.frm.nick.value = users[document.frm.users.selectedIndex];
		document.frm.groupsInUser.value = groupsInUser[document.frm.users.selectedIndex]
	}
	function update_groups() {
		document.frm.gname.value = groups[document.frm.groups.selectedIndex];
		document.frm.usersInGroup.value = usersInGroup[document.frm.groups.selectedIndex]
	}
	function check_group() {
		if (document.frm.gname.value == "") {
			alert("You must fill in the group name or select one group first.")
			return false
		}
		return true
	}
	function check_user() {
		if (document.frm.uname.value == "") {
			alert("You must fill in the user name or select one user first.")
			return false
		}
		return true
	}
	function check_usergroup() {
		if (check_user() && check_group())
			return true
		else
			return false
	}
	</script>
	<form name=frm action="/cgi-bin/usersgroups_proc.cgi" method="post">
	<table border=$BRD><tr><td>
	
	<fieldset><legend><strong>Users</strong></legend>
	<table border=$BRD>
EOF

IFS=":" # WARNING: for all the script
#account:password:UID:GID:GECOS:directory:shell
cnt=0; jstr=""
echo "<tr><td colspan=2><select multiple style=\"width:40ex\" size=\"8\" name=\"users\" onChange=\"update_users()\">"
while read user upass uid ugid uname dir shell;do
	if test "${user:0:1}" = "#" -o -z "$user" -o -z "$uid" -o -z "$uname"; then continue; fi
	if test $shell = "/bin/false"; then continue; fi
	if test $uid -lt 100; then continue; fi
	echo "<option>$uname</option>"
	jstr="$jstr; users[$cnt]=\"$user\"; groupsInUser[$cnt]=\"$(id -Gn $user)\";"
	cnt=$((cnt+1))
done < $CONFP
echo "</select></td></tr>"
num_users=$cnt

cat<<-EOF
	<tr><td>User name</td><td><input type=text size=12 name=uname></td></tr>
	<tr><td>Groups this user belongs to:</td>
		<td><textarea cols=12 rows=2 name=groupsInUser readonly></textarea></td></tr>
	<tr><td><input type=submit name=new_user value=NewUser>
		<input type=submit name=change_pass value=ChangePass onclick="return check_user()">
		<td><input type=submit name=del_user value=DelUser onclick="return check_user()"></td>
	</tr></table></fieldset>
	<input type=hidden size=12 name=nick>
	</td><td>
<script type="text/javascript"> $jstr </script>
	<fieldset><legend><strong>Groups</strong></legend>
	<table border=$BRD>
EOF

#group_name:passwd:GID:user_list
cnt=0; jstr=""
echo "<tr><td colspan=2><select multiple style=\"width:40ex\" size=\"8\" name=\"groups\" onChange=\"update_groups()\">"
while read group gpass ggid userl; do
	if test "${group:0:1}" = "#" -o "$gpass" = "!" -o -z "$group"; then continue; fi
	if test $ggid -lt 100; then continue; fi
	echo "<option>$group</option>"

	# primary group
	ul=$(awk -F: '{if ($4 == '$ggid' && substr($0, 1, 1) != "#") printf "%s," $1}' $CONFP)

	# plus suplementary groups, remove dups
	ul=$(echo -e "$userl,$ul" | tr ',' '\n' | sort -u | tr '\n' ':')

	un="" # get user name
	for i in $ul; do 
		un="$(awk -F: '/^'$i':/{printf "%s, ", $5}' $CONFP)${un}"
	done

	jstr="$jstr; groups[$cnt]=\"$group\"; usersInGroup[$cnt]=\"$un\";"
	cnt=$((cnt+1))
done < $CONFG
echo "</select></td></tr>"
num_groups=$cnt

cat <<-EOF
	<tr><td>Group name</td><td><input type=text size=12 name=gname></td></tr>
	<tr><td>Users belonging to this group:</td>
		<td><textarea cols=12 rows=2 name=usersInGroup readonly></textarea></td></tr>
	<tr><td><input type=submit name=new_group value=NewGroup onclick="return check_group()"></td>
	    <td><input type=submit name=del_group value=DelGroup onclick="return check_group()"></td></tr>
	</table></fieldset>
	</td></tr></table><br>
<script type="text/javascript"> $jstr </script>	
	<fieldset><legend><strong>Users and Groups</strong></legend><table border=$BRD>
		<tr><td>Add selected user to selected group</td>
			<td><input type=submit name=addToGroup value=AddToGroup onclick="return check_usergroup()"></td></tr>
		<tr><td>Remove selected user from selected group</td>
			<td><input type=submit name=delFromGroup value=DelFromGroup onclick="return check_usergroup()"></td></tr>
	</table></fieldset>
EOF

echo "</form></body></html>"