{

    inputs = {
        nixpkgs.url = "nixpkgs/nixos-24.05";
    };

    description = "Chameleolyser";

    outputs = { self, nixpkgs }:
        let
            system = "x86_64-linux";
            pkgs = import nixpkgs { inherit system;};
        in {
            packages.${system} = {
                default = pkgs.perl; 
                # This install the necessary executables for all nodes
                bedtools = pkgs.bedtools;
                bwa = pkgs.bwa;
                gatk = pkgs.gatk;
                picard-tools = pkgs.picard-tools;
                # TODO lofreq
                samtools = pkgs.samtools;
            };
        };
}
