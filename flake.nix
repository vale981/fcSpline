{
  description = "A fast cubic spline interpolator for real and complex data.";


  inputs = {
    utils.url = "github:vale981/hiro-flake-utils";
    nixpkgs.url = "nixpkgs/nixos-unstable";
  };

  outputs = { self, utils, nixpkgs, ... }:
    (utils.lib.poetry2nixWrapper nixpkgs {
      name = "fcSpline";
      shellPackages = pkgs: with pkgs; [ pyright black ];
      poetryArgs = {
        projectDir = ./.;
      };
    });
}
