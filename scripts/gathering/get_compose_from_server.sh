for stack in $(ssh $1 "find /srv/docker/ -type f -maxdepth 2 -name docker-compose.yml"); do
  localpath=$(basename "$(dirname "$stack")")
  echo "Copying $stack to $localpath"
  #rsync -avz $1:"$localpath"/docker-compose.yml ./"$(basename "$localpath")"/
  mkdir "$localpath"
  scp -r $1:"$stack" ./"$localpath"/docker-compose.yml
done
