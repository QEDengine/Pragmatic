#pragma once

// Standard library
#include <vector>	// vector
#include <string>	// string

// Clang
#include <clang/Lex/Pragma.h>			// PragmaHandler
#include <clang/Lex/Preprocessor.h>		// PragmaHandlerRegistry

namespace QED { namespace Pragmatic
{
	class PreamblePragmaHandler : public clang::PragmaHandler
	{
		public: // Constructor
		PreamblePragmaHandler() : clang::PragmaHandler("preamble") { }

		public: // Clang functions
		void HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken);
	};
}} // namespace QED::Pragmatic
