// Source header
#include "Callbacks.hpp"
// Pragmatic
#include "Relations.hpp"


#define PREAMBLE_PRAGMA_TOKEN "preamble"

namespace QED::Pragmatic
{
	Callbacks::Callbacks(clang::Preprocessor& preprocessor) : preprocessor(preprocessor), sourceManager(preprocessor.getSourceManager()) { }

	void Callbacks::FileChanged(clang::SourceLocation Loc, clang::PPCallbacks::FileChangeReason Reason, clang::SrcMgr::CharacteristicKind FileType, clang::FileID PrevFID)
	{
		if (Reason == clang::PPCallbacks::EnterFile && FileType == clang::SrcMgr::CharacteristicKind::C_User)
		{
			llvm::outs() << sourceManager.getFileEntryForID(sourceManager.getMainFileID())->getName() << '\n';
		}
	}

	void Callbacks::EndOfMainFile()
	{
		// llvm::outs() << "end of main file" << '\n';
		Meta::Instance().Write(preprocessor);
	}

	void Callbacks::InclusionDirective
	(
		clang::SourceLocation HashLoc,
		const clang::Token &IncludeTok,
		clang::StringRef FileName,
		bool IsAngled,
		clang::CharSourceRange FilenameRange,
		clang::Optional<clang::FileEntryRef> File,
		clang::StringRef SearchPath,
		clang::StringRef RelativePath,
		const clang::Module *Imported,
		clang::SrcMgr::CharacteristicKind FileType
	)
	{
		if (Imported == nullptr && FileType == clang::SrcMgr::CharacteristicKind::C_User)
		{
			std::string path = NormalizePath(sourceManager.getFilename(HashLoc).str(), sourceManager.getFileManager().getFileSystemOpts().WorkingDir);
			IncludeCallback(path, RelativePath.str());
		}
	}

	PreamblePragmaHandler::PreamblePragmaHandler() : PragmaHandler(PREAMBLE_PRAGMA_TOKEN, {{}})
	{
		
	}

	bool PreamblePragmaHandler::CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation)
	{
		return true;
	}

	std::string PreamblePragmaHandler::Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics)
	{
		preprocessor.addPPCallbacks(std::make_unique<Callbacks>(preprocessor));
		return "";
	}
}