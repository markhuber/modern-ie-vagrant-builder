rm -f *.box && vagrant box list | cut -f1 -d' ' | grep IE | xargs -I name vagrant box remove name
