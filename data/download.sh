#!/bin/bash


YEAR_ORDINALS=("2009" ) #"2010" "2011" "2012" "2013" "2014" "2015" "2016", "2017", "2018", "2019", "2020"
MONTH_ORDINALS=("01") # "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12"
WAITFLAG="1" # prevent nifi from getting partially written files.
export srcDataDirRoot=raw/yellow-taxi


download_yellow_data()
{
  echo ">>> download_yellow_data"
  for year in ${YEAR_ORDINALS[@]}; 
  do
      for month in ${MONTH_ORDINALS[@]};
      do
          url="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_"$year-$month".csv"
          echo $url
          filename="`echo $url | sed 's/trip+data/ /g' |  awk '{print $2 }'`"
          echo $filename
          echo $srcDataDirRoot$filename
          wget $url -qO - | head -10000 >> $srcDataDirRoot$filename$WAITFLAG
          mv $srcDataDirRoot$filename$WAITFLAG $srcDataDirRoot$filename
      done 
          
  done  
}

download_yellow_data

