<?php 
class ViewResults extends SearchDB{
        public function __construct(){            
        }

        public function searchBAr(){
            $datas = $this->searchData();
            if (is_array($datas) || is_object($datas)){
                $ret = array();
                foreach($datas as $data){
                    $instrumentData = $this->getInstruments($data['id']);
                    $instruments = array();
                    if (is_array($instrumentData) || is_object($instrumentData)){
                        foreach($instrumentData as $instr) {
                            $instruments[] = $instr['name'];
                        }
                    }
                    
                    $artist = $this->getArtist($data['id']);
                    if (is_array($artist) || is_object($artist)) {
                        $artist = $artist[0]['name'];
                    }
                    $ret[] = array('id'=> $data['id'], 'Tempo'=> $data['Tempo'], 'Genre'=> $data['Genre'], 'Uploaddatum'=> $data['Uploaddatum'], 'Laenge'=> $data['Laenge'], 'Jahr'=> $data['Jahr'], 'Tonart'=> $data['Tonart'], 'Epoche'=> $data['Epoche'], 'Titel'=> $data['Titel'], 'Url' => $data['Url'], 'Kuenstler'=> $artist, 'Instrumente' => $instruments);
                }
            }else{
                echo "keine Daten gefunden";
            }
        $this->data = json_encode($ret);
        }

        //filter Tempo
        public function minTempo(){
            $datas = $this->getTempo();
            $minTempo = $datas[0]['Tempo'];
            return $minTempo;
        }
        public function maxTempo(){
            $datas = $this->getTempo();
            $maxTempo = $datas[count($datas)-1]['Tempo'];
            return $maxTempo;
        }

        //filter laenge
        public function minLaenge(){
            $datas = $this->getLaenge();
            $minLaenge = $datas[0]['laenge'];
            return $minLaenge;
        }
        public function maxLaenge(){
            $datas = $this->getLaenge();
            $maxLaenge = $datas[count($datas)-1]['laenge'];
            return $maxLaenge;
        }

        //filter Tonart
        protected function key(){
            $datas = $this->getKey();
            $key = $datas;
            return $key;
        }   
    }
?>