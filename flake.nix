{
  description = "A fast cubic spline interpolator for real and complex data.";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    mach-nix.url = "github:DavHau/mach-nix";
    flake-utils.url = "github:numtide/flake-utils";
  };

   outputs = { self, nixpkgs, flake-utils, mach-nix }:
     let
       python = "python39";
       pypiDataRev = "master";
       pypiDataSha256 = "041rpjrwwa43hap167jy8blnxvpvbfil0ail4y4mar1q5f0q57xx";
       devShell = pkgs:
         pkgs.mkShell {
           buildInputs = [
             (pkgs.${python}.withPackages
               (ps: with ps; [ black mypy ]))
             pkgs.nodePackages.pyright
           ];
         };

     in flake-utils.lib.eachSystem ["x86_64-linux"] (system:
       let
         pkgs = nixpkgs.legacyPackages.${system};
         mach-nix-wrapper = import mach-nix { inherit pkgs python pypiDataRev pypiDataSha256; };

         fcSpline = (mach-nix-wrapper.buildPythonPackage {
           src = ./.;
           pname = "fcSpline";
           version = "0.1";
           requirements = builtins.readFile ./requirements.txt;
         });

         pythonShell = mach-nix-wrapper.mkPythonShell {
           requirements = builtins.readFile ./requirements.txt;
         };

         mergeEnvs = envs:
           pkgs.mkShell (builtins.foldl' (a: v: {
             buildInputs = a.buildInputs ++ v.buildInputs;
             nativeBuildInputs = a.nativeBuildInputs ++ v.nativeBuildInputs;
           }) (pkgs.mkShell { }) envs);

       in {
         devShell = mergeEnvs [ (devShell pkgs) pythonShell ];
         defaultPackage = fcSpline;
         packages.fcSpline = fcSpline;
       });
}
