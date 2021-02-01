<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">
  <style>
      body {background-color: lightblue;}
      table {border-collapse: collapse; border: 2px solid black;}
      table th {text-align: left; background-color: #3a6070; color: #FFF; padding: 4px 30px 4px 8px;}
      table td {border: 2px solid black; padding: 4px 8px; background-color:dodgerblue; font-weight: bold;}
  </style>
</head>

<body>
<?php

    # --Help
    if (($argc == 2) && $argv[1] == '--help'){
        print "This script tests parser.php and interpret.py";
        exit(0);
    } 

    # Testing class
    $tester = new Testing();
    
    class Testing {

        private $arguments;

        public function __construct()
        {
            $this->arguments = processArgs();
            $this->document = new CreateHTML();
            $this->scandirectory($this->arguments["directory"]);
            $this->document->endtable();
        }

        # Scanning directories for files and other directories
        private function scandirectory($dir_path){
            foreach(glob($dir_path . '/*', GLOB_ONLYDIR) as $dir) {
                foreach(glob($dir . '/*.src') as $src_file) {
                    $filename = substr(basename($src_file),0,-4);
                    $filepath = substr($src_file,0,-4);
                    $this->testing($src_file, $filepath, $filename);
                  }
                if ($this->arguments["recursive"] == 1){
                    $this->scandirectory($dir);
                }
              }
            }
        

        # Tests parser/interpret depending on arguments
        private function testing($srcfile, $filepath, $filename){

            # Creating missing files
            if (!file_exists($filepath.".in")) { touch($filepath.".in"); }
            if (!file_exists($filepath.".out")) { touch($filepath.".out"); }
            if (!file_exists($filepath.".rc")) { 
                $rc = fopen($filepath.".rc", "w");
                fwrite($rc, "0");
                fclose($rc); 
            }
            
            # Getting rc
            $fp = fopen($filepath.".rc", "r");
            $expectedrc = fgets($fp);
            fclose($fp);

            # Creating temporary files
            $fp = fopen($filepath.".tmp", "w");
            fclose($fp);
            $fp = fopen($filepath.".itmp", "w");
            fclose($fp);

            # Testing interpret only
            if ($this->arguments["int-only"] == 1){
                exec("python3.8 ".$this->arguments["i-script"]." --source=\"$srcfile\" <\"$filepath.in\" > \"$filepath.tmp\"", $b, $rc);
                exec("diff -q \"$filepath.tmp\" \"$filepath.out\"", $a, $diff_val);
            } else if($this->arguments["parse-only"] == 1){ # Testing parser only
                exec("php7.4 ".$this->arguments["p-script"]." <\"$srcfile\" >\"$filepath.tmp\"");
                exec("java -jar ".$this->arguments["jexamxml"]." \"$filepath.tmp\" \"$filepath.out\"", $b, $rc);
                if ($rc == 0){
                    $diff_val = 0;
                } else {
                    $diff_val = 1;
                }
            } else { # Testing both parser and interpret
                exec("php7.4 ".$this->arguments["p-script"]." <\"$srcfile\" >\"$filepath.itmp\"");
                exec("python3.8 ".$this->arguments["i-script"]." --source=\"$filepath.itmp\" <\"$filepath.in\" > \"$filepath.tmp\"", $b, $rc);
                exec("diff -q \"$filepath.tmp\" \"$filepath.out\"", $a, $diff_val);
            }
            
            # Deleting temporary files
            unlink("$filepath.itmp");
            unlink("$filepath.tmp");
            
            # Putting result of testing into html
            $this->document->htmladdrow($filename, $expectedrc, $rc, $diff_val);

        }

    }

    # Creating HTML
    class CreateHTML {

        public function __construct(){
            $this->htmlhead();
        }

        # Creating H1 for Title and start of a table
        public static function htmlhead(){
            print "<h1>Result of testing parse.php and interpret.py</h1>\n";
            print "<table>\n";
            print "\t<tr>\n";
            print "\t\t<th> File name </th>\n";
            print "\t\t<th> expected exit code </th>\n";
            print "\t\t<th> Returned exit code </th>\n";
            print "\t\t<th> Status </th>\n";
            print "\t</tr>\n";
        }

        # Creating row for results
        public static function htmladdrow($filename,$expectedrc,$rc,$status){

            print "\t<tr>\n";
            print "\t\t<td> $filename </td>\n";
            print "\t\t<td> $expectedrc </td>\n";
            print "\t\t<td> $rc </td>\n";
            if ($status == 0 && $expectedrc == $rc){
                $status = "OK";
                print "\t\t<td style=\"background-color:green\"> $status </td>\n";
            } else {
                $status = "FAIL";
                print "\t\t<td style=\"background-color:red\"> $status </td>\n";
            }
            
            print "\t</tr>\n";
        }

        # Ending table
        public static function endtable(){
            print "</table>\n";
        }

    }


    # Processing Arguments
    function processArgs(){
        global $argc;
        
        if ($argc > 1) {
            
            $possible_arguments = array("directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:");
            $arguments = getopt(null, $possible_arguments);
            # Setting arguments
            if (isset($arguments["recursive"])){ $arguments["recursive"] = 1; } else { $arguments["recursive"] = 0;}
            if (!isset($arguments["directory"])){ $arguments["directory"] = "./";} # If not set setting directory to root dir
            if (!isset($arguments["parse-script"])){$arguments["p-script"] = "./parse.php";} else {$arguments["p-script"] = $arguments["parse-script"];}
            if (!isset($arguments["int-script"])){ $arguments["i-script"] = "./interpret.py";} else {$arguments["i-script"] = $arguments["int-script"];}
            if (isset($arguments["parse-only"])){ $arguments["parse-only"] = 1;} else {$arguments["parse-only"] = 0;}
            if (isset($arguments["int-only"])){ $arguments["int-only"]= 1;} else  {$arguments["int-only"] = 0;}
            if (!isset($arguments["jexamxml"])){ $arguments["jexamxml"] = "/pub/courses/ipp/jexamxml/jexamxml.jar";}
            
            # Checking for incompatible combinations
            if (($arguments["parse-only"] == 1 && $arguments["int-only"] == 1) || ($arguments["parse-only"] == 1 && isset($arguments["int-script"]))){
                fwrite(STDERR, "Cannot use int-only or int-script with parse-only!");
                exit(10);}
            if (($arguments["int-only"] == 1 && $arguments["parse-only"] == 1) || ($arguments["int-only"] == 1 && isset($arguments["parse-script"]))){
                fwrite(STDERR, "Cannot use parse-only or parse-script with int-only!");
                exit(10);}
            if (!is_dir($arguments["directory"])){ fwrite(STDERR, "Could not find directory!"); exit(11); }
            
            return $arguments;
        } else {
            fwrite(STDERR, "Wrong number of arguments!");
            exit(10);
        }

    }  
    
?>
</body>
</html>